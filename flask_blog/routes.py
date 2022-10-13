import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flask_blog.forms import PostForm
from flask_blog import app, db
from flask_blog.models import Posts

@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=6)

    return render_template('home.html', posts=posts)


@app.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        picture_file = 'default.jpg'
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        post = Posts(title=form.title.data, content=form.content.data, image_file=picture_file)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',form=form, legend='New Post')

@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Posts.query.get(post_id)
    return render_template('post.html', title=post.title, post=post)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_file = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/posts', picture_file)

    output_size = (500, 500)
    img = Image.open(form_picture)
    img.resize(output_size)
    img.save(picture_path)

    return picture_file

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def update(post_id):
    post= Posts.query.get(post_id)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('The post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('update.html', title='update', form=form, legend='Update Post', post=post)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
def delete(post_id):
    post = Posts.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
