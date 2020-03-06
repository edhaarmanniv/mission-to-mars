from mission_to_mars import *
from flask import Flask, render_template, jsonify, redirect
import pymongo
import jinja2

CONN = "mongodb://localhost:27017"
client = pymongo.MongoClient(CONN)
db = client.marsDB

app = Flask(__name__)


@app.route("/")
def index():
    mars_info = db.mars_data.find_one()
    return render_template("index.html", mars_info=mars_info)


@app.route("/scrape")
def scrape_and_mongo():
    mars_json = scrape()
    db.mars_data.update({}, mars_json, upsert=True)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
