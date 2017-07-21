from flask import Blueprint,render_template, abort, redirect, safe_join, send_from_directory
from flask import request, session, url_for,flash
from werkzeug.utils import secure_filename
from LibServer import app
from LibServer import is_authenticated,sign_auth_path

 
import os.path
import os


browser=Blueprint('browser',__name__,template_folder='templates')

#
# The filesystem browser is based around a simple tree viewer.
# The option storage.path (string) controls where the base of
# the filesystem browser should reside.
#
# There's a few gotchas here and there. One is that the filesizes
# Are always going to be "human" sizes, in GiB (the "GigaOctets" style)
# used in base-8 calculations, as opposed to base-10 (SI) measurements.
#

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

@browser.route("/browse/")
@browser.route("/browse/<path:where>")
def browse(where=""):
    """
    This takes a path and turns it into a list of folders, etc.
    """
    basepath=app.config.get("storage", "location")
    

    #TODO: Make this something meaningful. There needs to be a good explanation as to what has happened
    # to the user instead of just shoving a "We don't find anything here" message.
    if(os.path.exists(os.path.join(basepath,'.uninitialized'))):
        abort(500)
    
    
    # Now, we're going to join the two together and normalize path
    fullpath = safe_join(basepath, where)

    # TODO: This could be nicer. 
    if(not os.path.exists(fullpath)):
        abort(404)
    

    # Now, we can read through the directory.
    dir_contents = list( filter(lambda fn: not fn.startswith("."), os.listdir(fullpath)))

    folder_description = None
    # check if there's a _folder.jpg and/or _index.txt file:
    if "_index.txt" in dir_contents:
        # _index.txt is there. We're going to get its contents and do the thing
        with open(os.path.join(fullpath,"_index.txt")) as f:
            folder_description = f.read()
    
    # not sure if I should do this, but it's a handy feature
    # maybe add a tunable?
    #if "index.html" in dir_contents:
    #    return redirect("getfile", file=safe_join(where,"index.html"))

    # Separate the files from the directories.
    # We do this so that we can show the directories first, then the files.
    # We also do this so that we can (maybe later?) show a sidebar with files vs.
    # a list of files + directories-- maybe even have them at the same time?
    dirs = list(filter(lambda o: os.path.isdir(os.path.join(fullpath,o)), dir_contents))
    files = list(filter(lambda o: os.path.isfile(os.path.join(fullpath,o)), dir_contents))

    # We're now going to split apart the path so that we can build breadcrumbs.
    # This might not really be the *worst* option, but
    # TODO: This probably could use some refinement.
    splits = where.lstrip('/').rstrip('/').split('/')
    crumbs = []
    # We're going to keep our current path in. It's empty by default,
    # but we're going to solve that. 
    cWhere = ''
    for part in splits:
        if cWhere=='':
            cWhere = part
        else:
            cWhere = '/'.join([cWhere,part])
        crumbs.append( ( part, cWhere ) )
    
    # This function is what we're going to later pass into map() against all our files. We can expand
    # on it later if we need more information out of stat()
    def file_record_maker(filename):
        record = { "name": filename }
        if where == '':
            record["fullpath"] = filename
        else:
            record["fullpath"] = safe_join(where, filename)
        statx = os.stat(os.path.join(fullpath,filename))
        record["size"] = sizeof_fmt(statx.st_size)
        record["size_b"] = statx.st_size
        return record
    
    # And here we go, mapping it against all our files, sorted by name.
    file_records = list(map(file_record_maker, sorted(files)))

    # We check here if we should show the 'up' direction. 

    show_up = (where != '')

    # Now, render our directory listing.
    # There's not much else to say here. 
    return render_template("browser/listing.html",
        listing_files=file_records,
        listing_dirs=sorted(dirs),
        where=where.rstrip('/').lstrip('/'),
        show_updir=show_up,
        crumbs=crumbs,
        folder_description=folder_description,
        title="Browsing {0}".format(splits[-1])
        )


@browser.route("/content/<path:name>")
def fetch_file(name,attach=False):
    # get the safe path to where
    # stream the file to the browser
    basepath = app.config.get("storage", "location")
    return send_from_directory(basepath, name)

def pub_uploads():
    return app.config.get('general','allow_upload',False)
def can_upload():
    return is_authenticated() or pub_uploads()

def allowed_filename(name):
    if is_authenticated():
        return True
    if not name.contains('.'):
        return False
    if app.config.get('general','restrict_uploads',True) == False:
        return True
    file_ext = name.split('.')[-1]
    allowed_exts = app.config.get('general','allowed_filetypes','')
    return file_ext in allowed_exts

@browser.route("/upload/<path:path>",methods=['POST','GET'])
@browser.route('/upload/',methods=['POST','GET'])
def upload(path=""):
    """

    Uploads a file to a place.
    """
    # Check that uploads are OK
    if not can_upload():
        return redirect(sign_auth_path(request.full_path))
    if request.method=='POST':
        # handle uploaded files
        if not 'file' in request.files:
            abort(400) # General UA error
        file = request.files["file"]
        # We default to using the name of the file provided,
        # but allow the filename to be changed via POST details.
        fname = file.filename
        if 'name' in request.form:
            fname = request.form['name']
        safe_fname = secure_filename(fname)
        if not allowed_filename(safe_fname):
            abort(400) # General client error
        # We're handling a potentially dangerous path, better run it through
        # The flask path jointer.
        basepath=app.config.get("storage", "location")
        fullpath = safe_join(basepath, path)
        file.save(os.path.join(fullpath,fname))
        flash("File uploaded successfully")
        return redirect(url_for('browser.upload',path=path))
    else:
        return render_template("browser/upload.html",path=path,title="Upload Files")