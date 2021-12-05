#The import statements
from flask import  Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import html
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from bs4 import BeautifulSoup
#Forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, Label
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField
from helper_functions import upload_image
import base64
import os

app = Flask(__name__)
app.secret_key = 'ksjkdbjhwvryf7ksmdms'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

IMG_API_KEY = 'c20b9a20348541665dbd0c99a2c8f04d'

ckeditor = CKEditor(app)
Bootstrap(app)
db = SQLAlchemy(app)
#Data base
class Stories(db.Model):
    __tablename__ = 'stories'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(300), nullable=False)
    genre = db.Column(db.String(30), nullable=False)
    sub_genre = db.Column(db.String(120), nullable=True)
    story_details = db.relationship('StoryDetails', backref='stories')

class StoryDetails(db.Model):
    __tablename__ = 'details'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(20))
    story = db.Column(db.String(1000))
    image = db.Column(db.String(300),  nullable=True)
    story_id = db.Column(db.Integer,  db.ForeignKey('stories.id'))

class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(40))
    url = db.Column(db.String(300))

db.create_all()

##WTForm
class CreateStoryForm(FlaskForm):
    title = StringField("Blog Post Title")
    img_url = StringField("Blog Image URL")
    story = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class CreateStoryBookForm(FlaskForm):
    title = StringField("Name")
    img_url = FileField("Image Url")
    img_url1 = StringField("Image Url")
    lable = Label(text='OR', field_id=1)
    genre = StringField("genre")
    story = CKEditorField("Details", validators=[DataRequired()], default='Hello')
    submit = SubmitField("Submit Post")


#API methods
# @app.route('/insert')
# def insert_stories():
#     story = Stories(name='Tortoise', image='https://pixy.org/src2/600/6007376.jpg', genre='African',
#                 )
#     db.session.add(story)
#     db.session.commit()
#     return jsonify('Status 200')

@app.route('/fetch', methods=['GET'])
def fetch():
    url = request.args.get('search')
    genre = request.args.get('genre')
    if url == None:
        stories = Stories.query.all()
    else:
        stories = Stories.query.filter(Stories.name.like(url+'%')).all()
    data = []
    for i in stories:
        id = i.id
        stories = StoryDetails.query.filter_by(story_id=id).all()
        story = [{'id':0, 'fake':'fake'}]
        for st in stories:
            story.append(
                {
                    'id': st.id,
                    'name': st.title,
                    'image': st.image,
                    'pages': st.story
                }
            )
        data.append({
            'id': i.id,
            'name': i.name,
            'genre': i.genre,
            'image': i.image,
            'story': story
        })


    rata = jsonify({'data': data})
    rata.headers.add("Access-Control-Allow-Origin", "*")
    return rata


@app.route('/fetch_genre', methods=['GET'])
def fetch_popular():
    url = request.args.get('search')
    genre = request.args.get('genre')
    print(genre)
    print(url)
    if url == None:
        stories = Stories.query.all()
    else:
        stories = Stories.query.filter(Stories.name.like(url+'%')).filter_by(genre=genre).all()
    data = []
    for i in stories:
        id = i.id
        stories = StoryDetails.query.filter_by(story_id=id).all()
        data.append({
            'id': i.id,
            'name': i.name,
            'genre': i.genre,
            'image': i.image,
        })

    rata = jsonify({'data': data})
    rata.headers.add("Access-Control-Allow-Origin", "*")
    return rata

#
@app.route('/delete_page/<int:id>/<int:story_id>')
def delete_page(id, story_id):
    page = StoryDetails.query.get(id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('detail', id=story_id))


#Story details fetch and post
@app.route('/insert_detail')
def insert_detail():
    detail = StoryDetails(title='Tilo', story='A long time ago', image='https://pixy.org/src2/600/6007376.jpg', story_id=1)
    db.session.add(detail)
    db.session.commit()
    return jsonify('Status: 200')
#fetch the details of a particular story using id
@app.route('/fetch_detail/<int:id>')
def fetch_detail(id):
    stories = StoryDetails.query.filter_by(story_id=int(id)).all()
    data = [{'id': 0, 'fake': 'fake'}]
    index = 1
    for st in stories:
        data.append({
            'id': st.id,
            'name': st.title,
            'image': st.image,
            'story': st.story
        })
        index += 1
    print(data)
    rata = jsonify({'data': data})
    return rata

@app.route('/fetch_stories')
def fetch_stories():
    pass



#Admin backend methods
@app.route('/')
def home():
    stories = Stories.query.all()
    data = [{'index': 0, 'id': 0,
            'name': 'New',
            'genre': 'new',
            'image': 'new'}]
    index = 1
    for i in stories:
        print(i.image)
        data.append({
            'index': index,
            'id': i.id,
            'name': i.name,
            'genre': i.genre,
            'image': i.image
        })
        index += 1
    rata = jsonify({'data': data})
    return render_template('stories.html', data=data)

@app.route('/detail/<int:id>')
def detail(id):
    stories = StoryDetails.query.filter_by(story_id=id).all()
    story_name = Stories.query.get(id)
    data = []
    index = 1
    for i in stories:
        story_soup = BeautifulSoup(i.story, 'html.parser')
        data.append({
            'index': index,
            'id': i.id,
            'title': i.title,
            'image': i.image,
            'story': story_soup.get_text()
        })
        index += 1
    print(data)
    rata = jsonify({'data': data})
    return render_template('index.html', details=data, story_id=id, story_name=story_name.name)


@app.route("/new-post/<int:id>", methods=['GET', 'POST'])
def add_new_post(id):
    form = CreateStoryForm()
    if form.validate_on_submit():
        new_Story = StoryDetails(
            title=form.title.data,
            image= form.img_url.data,
            story=form.story.data,
            story_id=id
        )
        print(new_Story)
        db.session.add(new_Story)
        db.session.commit()
        return redirect(url_for("detail", id=id))
    return render_template("add_story.html", form=form, is_edit=True)




@app.route("/edit-post/<int:id>/<int:story_id>", methods=['GET', 'POST'])
def edit_post(id, story_id):
    story = StoryDetails.query.get(id)
    form = CreateStoryForm(
        title=story.title,
        story=story.story,
        img_url=story.image
    )
    if form.validate_on_submit():
        story.title=form.title.data
        story.image= form.img_url.data
        story.story=form.story.data
        db.session.commit()
        return redirect(url_for("detail", id=story_id))
    return render_template("add_story.html", form=form, is_edit=False)


@app.route("/new-story", methods=['GET', 'POST'])
def add_new_story():
    form = CreateStoryBookForm()
    if form.validate_on_submit():
        imago = ''
        if form.img_url1.data != '':
            print('a url upload')
            imago = upload_image(form.img_url1.data, IMG_API_KEY)
        else:
            data = form.img_url.data
            print(data)
            image_b64 = base64.b64encode(data.read())
            imago = upload_image(image_b64, IMG_API_KEY)


        new_Story = Stories(
            name=form.title.data,
            image=imago,
            genre=form.story.data,
        )
        print(new_Story)
        db.session.add(new_Story)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_st.html", form=form, is_edit=False)

@app.route("/edit-story/<int:id>", methods=['GET', 'POST'])
def edit_story(id):
    story = Stories.query.get(id)
    form = CreateStoryForm(
        title=story.name,
        story=story.genre,
        img_url=story.image
    )
    if form.validate_on_submit():
        # if form.img_url.data != None :
        #     data = form.img_url.data
        #     print(data)
        #     image_b64 = base64.b64encode(data.read())
        #     image = upload_image(image_b64, IMG_API_KEY)
        # else:
        #     image = upload_image(form.img_url1.data, IMG_API_KEY)
        story.name=form.title.data
        story.image=form.img_url.data
        story.genre=form.story.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_st.html", form=form, is_edit=True)


#Upload story art to the site
@app.route('/story_art')
def story_art():
    return render_template('image.html')

if __name__ == '__main__':
    app.run(debug=True)