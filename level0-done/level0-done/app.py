from flask.ext.mongoengine import MongoEngine
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'books' }

db = MongoEngine(app)
class FavoriteBook(db.Document):
	author = db.StringField(required=True)
	title = db.StringField(required=True)
	link = db.StringField(required=True)
@app.route("/name")
def name():
	return "Manu Gandham"

@app.route("/favorite/<id>")
def favorite(id):
	book_url = "https://www.googleapis.com/books/v1/volumes/"+id
	book_dict = requests.get(book_url).json()
	new_fav = FavoriteBook(author=book_dict["volumeInfo"]["authors"][0], title=book_dict["volumeInfo"]["title"], link=book_url)
	new_fav.save()
	return render_template("confirm.html", api_data=book_dict)

@app.route("/")
def hello():
	return render_template("hello.html")

@app.route("/<alias>")
def general(alias):
	return "Hello World!"+alias

@app.route("/website")
def website():
	return "www.github.com/mgandham"

@app.route("/search",methods=["POST", "GET"])
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
	
