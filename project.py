from flask import Flask , render_template, request, redirect, url_for, flash, \
   jsonify
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError
from wtforms import StringField, SubmitField, PasswordField, BooleanField, \
   IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, \
   ValidationError
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
   login_required, current_user
from flask import session as login_session
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, ForeignKey, Integer, String
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Catalogue"

# CSRF Config
app.config.update(
        SECRET_KEY='a random string',
        SQLALCHEMY_DATABASE_URI=('sqlite:///bookcatalogue.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

# CRUD Operations
from database_setup import Base, Book, Publication
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///bookcatalogue.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# App configuration
db = SQLAlchemy()
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
#login_manager.init_app(app)
login_manager.login_view = 'showLogin'
login_manager.session_protection = 'strong'
#bcrypt = Bcrypt(app)
db.init_app(app)

#@login_manager.user_loader
#def load_user(id):
#    return User.query.get(int(id))

# Classes begin
class EditBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    avg_rating = StringField('Average Rating Out of 5',
                             validators=[DataRequired()])
    format = StringField('Format', validators=[DataRequired()])
    img_url = StringField('Image')
    num_pages = StringField('Pages', validators=[DataRequired()])
    pub_id = IntegerField('PublisherID', validators=[DataRequired()])
    submit = SubmitField('Update')

class CreateBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    avg_rating = FloatField('Rating out of 5', validators=[DataRequired()])
    format = StringField('Format', validators=[DataRequired()])
    img_url = StringField('Image')
    num_pages = IntegerField('Pages', validators=[DataRequired()])
    pub_id = IntegerField('PublisherID', validators=[DataRequired()])
    submit = SubmitField('Create')

class Publication(db.Model):
    __tablename__ = 'publication'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Publisher is {}'.format(self.name)

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    author = db.Column(db.String(350))
    avg_rating = db.Column(db.Float)
    format = db.Column(db.String(50))
    image = db.Column(db.String(100), nullable=True, unique=True)
    num_pages = db.Column(db.Integer)
    pub_date = db.Column(db.String(50), default=datetime.now())

    # Relationship
    pub_id = db.Column(db.Integer, db.ForeignKey('publication.id'))

    def __init__(self, title, author, avg_rating, book_format, image, num_pages,
                 pub_id):
        self.title = title
        self.author = author
        self.avg_rating = avg_rating
        self.format = book_format
        self.image = image
        self.num_pages = num_pages
        self.pub_id = pub_id

    def __repr__(self):
        return '{} by {}'.format(self.title, self.author)

# Routes begin
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current users token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/')
def display_books():
    books = session.query(Book).all()

    return render_template('home.html', books=books)

@app.route('/display/publisher/<publisher_id>')
def display_publisher(publisher_id):
    publisher = session.query(Publication).filter_by(id=publisher_id).first()
    publisher_books = session.query(Book).filter_by(pub_id = publisher.id).all()

    return render_template('publisher.html', publisher=publisher,
                           publisher_books=publisher_books)

@app.route('/book/delete/<book_id>', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if request.method == 'POST':
        db.session.delete(book)
        db.session.commit()
        flash('book deleted successfully')
        return redirect(url_for('display_books'))
    return render_template('delete_book.html', book=book, book_id=book.id)

@app.route('/book/edit/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get(book_id)
    form = EditBookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.avg_rating = form.avg_rating.data
        book.format = form.format.data
        book.num_pages = form.num_pages.data
        db.session.add(book)
        db.session.commit()
        flash('book edited successfully')
        return redirect(url_for('display_books'))
    return render_template('edit_book.html', form=form)

@app.route('/create/book/<pub_id>' , methods=['GET', 'POST'])
@login_required
def create_book(pub_id):
    form = CreateBookForm()
    form.pub_id.data = pub_id  # pre-populates pub_id
    if form.validate_on_submit():
        book = Book(title=form.title.data, author=form.author.data,
                    avg_rating=form.avg_rating.data,
                    book_format=form.format.data, image=form.img_url.data,
                    num_pages=form.num_pages.data,
                    pub_id=form.pub_id.data)
        db.session.add(book)
        db.session.commit()
        flash('book added successfully')
        return redirect(url_for('display_publisher', publisher_id=pub_id))
    return render_template('create_book.html', form=form, pub_id=pub_id)
# Routes end

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
