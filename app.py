from flask.ext.mongoengine import MongoEngine
#from mongoengine import connect
from wtforms import PasswordField, Form, BooleanField, TextField, validators
from flask import Flask, render_template, request, redirect, flash
import requests
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'aliases' }
app.config['SECRET_KEY'] = 'take them glasses off and get in the pool'
app.config['WTF_CSRF_ENABLED'] = True
#connect('db',host='mongodb://heroku_jkth7wxw:khf2ufn8j1s9ch8qb64dqq6819@ds059185.mongolab.com:59185/heroku_jkth7wxw')
db = MongoEngine(app)

class LoginForm(Form):
	plaintext = TextField('Alias',[validators.Required(), validators.length(min=6, max=18)])
	password = PasswordField('New Password', [validators.Required(), validators.length(min=6, max=18)])

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
				return render_template("edit_profile.html",alpha=registered_alias[0])
			else:
				# alias's password doesn't match (might have expired)
				return redirect("/login")
		else:
			# alias is not registered, in which case register it
			new_alias = Alias(plaintext = form.plaintext.data, password = "DUMMY92", location="", beacon_w = False, beacon_p = False, beacon_z = False, timestamp="")
			new_alias.save()
			newly_registered_alias=Alias.objects(plaintext=new_alias.plaintext)
			return render_template("edit_profile.html",alpha=newly_registered_alias[0])
	else:
		return render_template("login.html", form=form)

@app.route("/favorite/<id>")
def favorite(id):
	book_url = "https://www.googleapis.com/books/v1/volumes/"+id
	book_dict = requests.get(book_url).json()
	poster = User.objects(name=current_user.name).first()
	new_fav = FavoriteBook(author=book_dict["volumeInfo"]["authors"][0], title=book_dict["volumeInfo"]["title"], link=book_url, poster=poster)
	new_fav.save()
	return render_template("confirm.html", api_data=book_dict)

@app.route("/favorites")
def favorites():
	current_poster = User.objects(name=current_user.name).first()
	favorites = FavoriteBook.objects(poster=current_poster);
	return render_template("favorites.html", current_user=current_user, favorites=favorites)

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/<alias>")
def general(alias):
	beta = Alias.objects(plaintext=alias);
	if len(beta)>=1:
		return render_template("profile.html",beta=beta[0])
	else:
		form = LoginForm(request.form)
		form.plaintext.data = alias 
		return render_template("login.html",form=form)

if __name__ == "__main__":
	app.run(host="0.0.0.0",port=int(os.environ.get('PORT',5000)))
	
