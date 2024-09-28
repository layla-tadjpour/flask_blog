from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from myblog.auth import login_required
from myblog.model import Post
from myblog import db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    posts = Post.get_all_posts()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            try:
                post = Post.create_post(g.user.id, title, body)
                db.session.commit()
                return redirect(url_for('blog.index'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating post: {str(e)}")
                flash("An error occurred while creating the post. Please try again.")

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = Post.get_post(id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            try:
                updated_post = Post.update_post(id, title, body)
                if updated_post:
                    db.session.commit()
                    flash('Post updated successfully.')
                    return redirect(url_for('blog.index'))
                else:
                    flash('Post not found.')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating post: {str(e)}")
                flash('An error occurred while updating the post. Please try again.')


    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    try:
        post = Post.delete_post(id)
        if post:
            db.session.commit()
            flash('Post deleted successfully.')
        else:
            flash('Post not found.')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting post: {str(e)}")
        flash('An error occurred while deleting the post. Please try again.')


    return redirect(url_for('blog.index'))