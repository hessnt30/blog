from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from jinja2 import UndefinedError
from .models import Post, User, Comment, Like, Band
from . import db

views = Blueprint("views", __name__)


@views.route("/news")
@login_required
def news():
    return render_template("news.html", user=current_user, is_Authenticated=is_Authenticated)

@views.route("/")
@views.route("/feed")
@login_required
def feed():
    posts = Post.query.all()
    return render_template("feed.html", user=current_user, band=current_user, posts=posts, is_Authenticated=is_Authenticated)

@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty.', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created', category='success')
            return redirect(url_for('views.feed'))

    return render_template("create_posts.html", band=current_user, is_Authenticated=is_Authenticated)

@views.route("/delete-post/<post_id>")
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for("views.feed"), is_Authenticated=is_Authenticated)

# View all of a band's posts
@views.route("/posts/<username>")
@login_required
def posts(username):
    band = Band.query.filter_by(username=username).first()

    if not band:
        flash('No such band.', category='error')
        return redirect(url_for('views.feed'))
    
    posts = band.posts
    return render_template("posts.html", band=current_user, posts=posts, username=username, is_Authenticated=is_Authenticated)

@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.feed'), is_Authenticated=is_Authenticated)

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user != comment.post.author:
        flash('You are not authorized to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for("views.feed"), is_Authenticated=is_Authenticated)

@views.route("/like-post/<post_id>", methods=['GET'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id)

    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        flash('Post does not exist.', category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        
    return redirect(url_for('views.feed'), is_Authenticated=is_Authenticated)

def is_Authenticated(user, band):
    try: 
        if user.is_authenticated:
            return True
    except: 
        if band.is_authenticated:
            return True
    else:
        return False