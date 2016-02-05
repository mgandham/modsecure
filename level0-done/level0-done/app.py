from flask.ext.mongoengine.wtf import model_form
from wtforms import PasswordField
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.mongoengine import MongoEngine
from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'books' }
app.config['SECRET_KEY'] = 'take them glasses off and get in the pool'
app.config['WTF_CSRF_ENABLED'] = True
db = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Document):
	name = db.StringField(required=True,unique=True)
	password = db.StringField(required=True)
	def is_authenticated(self):
		user = User.objects(name=self.name, password=self.password)
		return len(users) != 0
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return self.name
UserForm = model_form(User)
UserForm.password = PasswordField('password')
@login_manager.user_loader
def load_user(name):
	users = User.objects(name=name)
	if len(users) != 0:
		return users[0]
	else:
		return None

class Alias(db.Document):
	plaintext = db.StringField(required=True,unique=True)
	password = db.StringField(required=True)
	location = db.StringField
	beacon_w = db.BooleanField
	beacon_p = db.BooleanField
	beacon_z = db.BooleanField
	timestamp = db.DateTimeField
	def is_authenticated(self):
		alias = Alias.objects(name=self.name, password=self.password)
		return len(alias) != 0
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return self.name

class FavoriteBook(db.Document):
	author = db.StringField(required=True)
	title = db.StringField(required=True)
	link = db.StringField(required=True)
	poster = db.ReferenceField(User)

@app.route("/logout")
def logout():
	logout_user()
	return redirect("/")

@app.route("/login", methods=['GET', 'POST'])
def login():
	form = UserForm(request.form)
	if request.method == 'POST' and form.validate():
		registered_users = User.objects(name=form.name.data,password=form.password.data)
		if len(registered_users) == 0:
			return redirect('/login')
		else:
			login_user(registered_users[0])
			return redirect('/search')
	return render_template('login.html', form=form)

@app.route("/name")
def name():
	return "Manu Gandham"

@app.route("/favorite/<id>")
@login_required
def favorite(id):
	book_url = "https://www.googleapis.com/books/v1/volumes/"+id
	book_dict = requests.get(book_url).json()
	poster = User.objects(name=current_user.name).first()
	new_fav = FavoriteBook(author=book_dict["volumeInfo"]["authors"][0], title=book_dict["volumeInfo"]["title"], link=book_url, poster=poster)
	new_fav.save()
	return render_template("confirm.html", api_data=book_dict)

@app.route("/favorites")
@login_required
def favorites():
	current_poster = User.objects(name=current_user.name).first()
	favorites = FavoriteBook.objects(poster=current_poster);
	return render_template("favorites.html", current_user=current_user, favorites=favorites)

@app.route("/")
def hello():
	return render_template("hello.html")

@app.route("/<alias>")
def general(alias):
	return "Hello World!"+alias

@app.route("/website")
def website():
	return "www.github.com/mgandham"

@app.route("/register", methods=["POST", "GET"])
def register():
	form = UserForm(request.form)
	if request.method == 'POST' and form.validate():
		form.save()
		return redirect("/login")
	else:
		return render_template("register.html", form=form)

@app.route("/search",methods=["POST", "GET"])
@login_required
def search():
	if request.method == "POST":
		# User has used the search box
		url = "https://www.googleapis.com/books/v1/volumes?q=" + request.form["user_search"]
		response_dict = requests.get(url).json()
		return render_template("results.html",api_data=response_dict)
	else:
		# User is loading the page
		return render_template("search.html") 

if __name__ == "__main__":
	app.run(host="0.0.0.0")
	
