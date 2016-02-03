from flask import Flask, render_template

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/name")
def name():
	return "Manu Gandham"

@app.route("/hello")
def hello():
	return render_template("hello.html")

@app.route("/<alias>")
def general(alias):
	return "Hello World!"+alias

@app.route("/website")
def website():
	return "www.github.com/mgandham"

@app.route("/search")
def search():
	return render_template("search.html") 

if __name__ == "__main__":
	app.run(host="0.0.0.0")
	
