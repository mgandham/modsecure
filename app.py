from flask.ext.mongoengine import MongoEngine
from mongoengine import connect
from wtforms import PasswordField, Form, BooleanField, TextField, validators
from flask import Flask, render_template, request, redirect, flash
import requests
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'aliases' }
app.config['SECRET_KEY'] = 'take them glasses off and get in the pool'
app.config['WTF_CSRF_ENABLED'] = True
connect('db',host='mongodb://heroku_jkth7wxw:khf2ufn8j1s9ch8qb64dqq6819@ds059185.mongolab.com:59185/heroku_jkth7wxw')
db = MongoEngine(app)

class LoginForm(Form):
	plaintext = TextField('Alias',[validators.Required(), validators.length(min=6, max=18)])
	password = PasswordField('New Password', [validators.Required(), validators.length(min=6, max=18)])

class Alias(db.Document):
	plaintext = db.StringField(min_length=6,max_length=18,required=True,primary_key=True,unique=True)
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

@app.route("/submit", methods=['POST'])
def update():
	print request.form
	if request.form["switch_w"] != None:
		beacon_w=True
	else:
		beacon_w=False
	if request.form["switch_p"] != None:
		beacon_p=True
	else:
		beacon_p=False
	if request.form["switch_z"] != None:
		beacon_z=True
	else:
		beacon_z=False
#	if request.form["location_field"] != None:
#		location = request.form["location_field"]
#	else:
#		location = ""
		
	updated_alias=Alias(plaintext=request.form["alias_field"],location="",beacon_w=beacon_w,beacon_p=beacon_p,beacon_z=beacon_z)
	updated_alias.save()	
	jsonApi = APIJsonStock(updated_alias)
	jsonApiWeather = APIJsonIceCream(updated_alias)
	print(jsonApiWeather)
	return render_template("profile.html",beta=updated_alias, jsonLoc=jsonApi, jsonApiWeather=jsonApiWeather)
	
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
		jsonApi = APIJsonStock(beta[0])
		jsonApiWeather = APIJsonIceCream(beta[0])
		print(jsonApiWeather)
		return render_template("profile.html",beta=beta[0], jsonLoc=jsonApi, jsonApiWeather=jsonApiWeather)
	else:
		form = LoginForm(request.form)
		form.plaintext.data = alias 
		return render_template("login.html",form=form)
def APIJsonStock(beta):
#	if beta.beacon_w:
		url = "https://query.yahooapis.com/v1/public/yql?q=select%20Symbol%2C%20PreviousClose%2C%20Open%2C%20Volume%20%20%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(%20'YHOO'%2C%20'FB'%2C%20'MSFT'%2C%20'AMZN')&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
		response = requests.get(url)
		response_dict = response.json()
		return response_dict["query"]["results"]
#	else:
#		return {}

def APIJsonIceCream(beta):
#	if beta.beacon_p:
		url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22New%20York%2C%20NY%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
		response = requests.get(url)
		response_dict = response.json()
		return response_dict["query"]["results"]["channel"]["item"]["description"]
#	else:
#		return {}


if __name__ == "__main__":
	app.run(host="0.0.0.0",port=int(os.environ.get('PORT',5000)))
	
