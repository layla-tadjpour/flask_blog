from flask import Flask, request, render_template, redirect, url_for, abort
import time
from datetime import datetime
from db import Post

app = Flask(__name__)

p = Post() 


def render_front(num_past_posts=10):
    posts = p.fetchmany_ordered("created", num_past_posts)
    return render_template("front.html", posts=posts)
    
def render_form(subject="", content="", error = ""):
    return render_template("newpost.html", subject=subject, content=content, error=error)

def unix_time_now():
    now = datetime.now()
    return int(time.mktime(now.timetuple()))


@app.route("/blog/<int:post_id>")
def post_page(post_id):
    post = p.fetchone(where="where rowid = ?", params=(post_id,))
    if not post:
        abort(404)
    post_dict = {
        # first elem is rowid
        'subject': post[1],
        'content': post[2].replace('\n', '<br>'),
        'created': datetime.fromtimestamp(int(post[3])),
        # not used for now
        'last_modified': datetime.fromtimestamp(int(post[4]))
    }
    return render_template("permalink.html", post_dict=post_dict)
    

@app.route("/blog")
def get():
    return render_front(num_past_posts=10)

@app.route("/blog/newpost")
def get_newpost():
    return render_form()


@app.route("/blog/newpost", methods=['post'])
def post():
    subject = request.form.get("subject")
    content = request.form.get("content")
    if subject and content:
        post_id = p.put(subject, content, unix_time_now(), unix_time_now())
        return redirect(url_for("post_page", post_id=post_id))
    else:
        error = "subject and contect please!"
        return render_form(subject=subject, content=content, error=error)

