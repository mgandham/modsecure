from flask.ext.mongoengine import MongoEngine
from wtforms import PasswordField, Form, BooleanField, TextField, validators
from flask import Flask, render_template, request, redirect, flash
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
import requests

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'aliases' }
app.config['SECRET_KEY'] = 'take them glasses off and get in the pool'
app.config['WTF_CSRF_ENABLED'] = True
db = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)

class LoginForm(Form):
	plaintext = TextField('Alias',[validators.Required(), validators.length(min=6, max=18)])
	password = PasswordField('New Password', [validators.Required(), validators.length(min=6, max=18)])

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

@login_manager.user_loader
def load_user(name):
	users = User.objects(name=name)
	if len(users) != 0:
		return users[0]
	else:
		return None

class Alias(db.Document):
	plaintext = db.StringField(min_length=6,max_length=18,required=True,unique=True)
	password = db.StringField(min_length=6, max_length=18,required=True)
	location = db.StringField(required=False)
	beacon_w = db.BooleanField(required=False)
	beacon_p = db.BooleanField(required=False)
	beacon_z = db.BooleanField(required=False)
	timestamp = db.StringField(required=False)
	def is_authenticated(self):
		alias = Alias.objects(plaintext=self.plaintext, password=self.password)
		return len(alias) != 0
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return self.plaintext

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
	form = LoginForm(request.form)
	if request.method == 'POST' and form.validate():
		registered_alias = Alias.objects(plaintext=form.plaintext.data)
		for alias in registered_alias:
			print alias.plaintext+ " test "+alias.password
		if len(registered_alias) >= 1:
			print('alias found in db')
			# alias is already registered, check if password matches
			if form.password.data == registered_alias[0].password:
				login_user(registered_alias[0])
				return redirect('/'+registered_alias[0].plaintext+'')
			else:
				# alias's password doesn't match (might have expired)
				return redirect('/login')
		else:
			# alias is not registered, in which case register it
			new_alias = Alias(plaintext = form.plaintext.data, password = "DUMMY92", location="", beacon_w = False, beacon_p = False, beacon_z = False, timestamp="")
			new_alias.save()
			flash('new alias saved')
			return redirect('/'+new_alias.plaintext+'')
	else:
		return render_template("login.html", form=form)
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
	
