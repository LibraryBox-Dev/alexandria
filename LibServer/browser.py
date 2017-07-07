from flask import Blueprint,render_template, abort, redirect, safe_join, send_from_directory
from LibServer import app
 
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

@browser.route("/")
@browser.route("/<path:where>")
def browse(where=""):
    """
    This takes a path and turns it into a list of folders, etc.
    """
    basepath=app.config.get("storage", "path")
    # Now, we're going to join the two together and normalize path
    fullpath = safe_join(basepath, where)
    # Now, we can read through the directory.
    dir_contents = list(os.listdir(fullpath))

    dirs = list(filter(lambda o: os.path.isdir(os.path.join(fullpath,o)), dir_contents))
    files = list(filter(lambda o: os.path.isfile(os.path.join(fullpath,o)), dir_contents))

    # Handle the files. We need each one to know its size and filename.

    def file_record_maker(filename):
        record = { "name": filename }
        statx = os.stat(os.path.join(fullpath,filename))
        record["size"] = sizeof_fmt(statx.st_size)
        record["size_b"] = statx.st_size
        return record
    
    file_records = list(map(file_record_maker, sorted(files)))

    # We get to cheat badly. Oh so badly. 
    # We need no way to handle getting the files! FANTASTIQUE! 

    # We do however need to include a way to handle showing "up a directory" and other fun stuff.

    show_up = False
    if(where != ""):
        show_up = True
    return render_template("browser/listing.html",
        listing_files=file_records,
        listing_dirs=sorted(dirs),
        where=where.rstrip('/').lstrip('/'),
        show_updir=show_up
        )


@browser.route("/getfile/<path:name>")
def fetch_file(name,attach=False):
    # get the safe path to where
    # stream the file to the browser
    basepath = app.config.get("storage", "path")
    return send_from_directory(basepath, name)