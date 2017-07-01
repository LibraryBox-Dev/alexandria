from flask import Blueprint,render_template, abort, redirect
from LibServer import app

browser=Blueprint('browser',__name__,template_folder='templates')


@browser.route('/')
def index():
    return render_template('index.html',
                           year=2017,
                           title=app.config["parser"].get("general","hostname")
                           )

# the browser is a simple file directory browser. It also handles the file
# upload capability. The upload capability depends on either there being a
# key in the session that is "admin" and which is set to True, or the global
# option "allow_uploads" to be set True.

# The filesystem for Alexandria is broken up into a handful of mountpoints.

@browser.route("/<collect>/<path:path>")
def browse(collect,path):
    """
    This takes a path and turns it into a list of folders, etc.
    """
    # we ignore collect for now. It's just going to be used as a prefix.
