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

    
@bp.route("/<int:year>/<int:month>/<int:day>/<slug>")
def get_page(year, month, day, slug, check_author=True):
    post = Post.get_post(slug)
    if not post or post.created.year != year or post.created.month != month or post.created.day != day:
        abort(404)
    return render_template("blog/permalink.html", post=post)


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
                return redirect(url_for('blog.get_page', 
                                        year=post.created.year, 
                                        month=post.created.month, 
                                        day=post.created.day, 
                                        slug=post.slug))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating post: {str(e)}")
                flash("An error occurred while creating the post. Please try again.")

    return render_template('blog/create.html')


@bp.route('/<slug>/update', methods=('GET', 'POST'))
@login_required
def update(slug):
    post = Post.get_post(slug)
    if post is None:
        abort(404, f"Post with slug {slug} doesn't exist.")

    if post.author_id != g.user.id:
        abort(403)

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
                updated_post = Post.update_post(slug, title, body)
                if updated_post:
                    db.session.commit()
                    flash('Post updated successfully.')
                    return redirect(url_for('blog.get_page', 
                                            year=updated_post.created.year, 
                                            month=updated_post.created.month, 
                                            day=updated_post.created.day, 
                                            slug=updated_post.slug))
                else:
                    flash('Post not found.')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating post: {str(e)}")
                flash('An error occurred while updating the post. Please try again.')


    return render_template('blog/update.html', post=post)


@bp.route('/<slug>/delete', methods=('POST',))
@login_required
def delete(slug):
    post = Post.get_post(slug)
    if post is None:
        abort(404, f"Post with slug {slug} doesn't exist.")

    # Check if the current user is the author of the post
    if post.author_id != g.user.id:
        abort(403)

    try:
        post = Post.delete_post(slug)
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