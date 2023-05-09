from flask import Flask, request, send_file, redirect, Response, jsonify
from flask_cors import CORS

import json 
import os 
import io
import csv
import pandas as pd 

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():

    return "Hello, cross-origin-world!"


@app.route('/get_data', methods=["GET"])
def get_csv():

    """ 
    Returns the csv file requested.
    """
    # Checking that the month parameter has been supplied
    if not "file" in request.args:
        return "You haven't specificed a file"

    month = request.args["file"]

    json_path = f"./static/{month}.json"   

    r = open(json_path)
    jsony = json.load(r)

    response = jsonify(jsony)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response



    # print(month)

    # # Also make sure the requested csv file does exist
    # if not os.path.isfile(csv_path):
    #     return f"ERROR: file {month} was not found on the server"
    # # Send the file back to the client
    # return send_file(csv_path, as_attachment=True)


# https://thambili.herokuapp.com/get_data?file=latest_foi

# http://127.0.0.1:5000/get_data?file=latest_foi

