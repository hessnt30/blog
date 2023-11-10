from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from sqlalchemy import DateTime
views = Blueprint("views", __name__)


@views.route("/news")
def news():
    return render_template("news.html", user=current_user)

@views.route("/")
@views.route("/feed")
def feed():
    posts = Post.query.order_by(Post.date).all()
    return render_template("feed.html", user=current_user, posts=posts)

@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        date = request.form.get('date')
        location = request.form.get('location')
        doors = request.form.get('doors')
        time = request.form.get('time')
        price = request.form.get('price')
        other_bands = request.form.get('who')
        description = request.form.get('description')

        year = date[0:4]
        month = date[5:7]
        day = date[8:10]

        date = month + "/" + day + "/" + year

        if not location or not time or not price:
            flash('Post cannot be empty.', category='error')
        else:
            post = Post(date=date,
                        location=location, 
                        doors=doors,
                        time=time, 
                        price=price, 
                        who=other_bands, 
                        details=description, 
                        author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created', category='success')
            return redirect(url_for('views.feed'))

    return render_template("create_posts.html", user=current_user)

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

    return redirect(url_for("views.feed"))

# View all of a user's posts
@views.route("/posts/<username>")
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No such band.', category='error')
        return redirect(url_for('views.feed'))
    
    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)

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

    return redirect(url_for('views.feed'))

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

    return redirect(url_for("views.feed"))

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
        
    return redirect(url_for('views.feed'))

@views.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)