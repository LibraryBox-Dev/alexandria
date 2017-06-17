from flask import Blueprint,render_template, abort, redirect

browser=Blueprint('browser',__name__,template_folder='templates')


@browser.route('/browse')
def index():
    return render_template('index.html',
                           year=2017,
                           title="hello"
                           )
