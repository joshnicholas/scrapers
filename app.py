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


@app.route('/check_archives', methods=["GET"])
def check_folders():
    if not "folder" in request.args:
        return "You haven't specificed a folder"
    folder = request.args["folder"]
    
    fillos = os.listdir(f"./archive/{folder}/daily_dumps")
    fillos = list(set(fillos))

    stringo = ''

    for thing in fillos:
        stringo += f"{thing}, "

    return stringo

@app.route("/get_archives", methods=['GET'])
def get_file():
    """ 
    Returns the csv file requested.
    """
        
    # Checking that the month parameter has been supplied

    if not "file" in request.args:
        return "You haven't specificed a file"
    
    pathos = request.args['pathos']
    fillo = request.args["file"]

    if "latest" in fillo:
        csv_path = f"./archive/{pathos}/latest.csv"
        return send_file(csv_path, as_attachment=True)
    else:
        csv_path = f"./archive/{pathos}/daily_dumps/{fillo}.csv"
        return send_file(csv_path, as_attachment=True)

# http://127.0.0.1:5000/get_archives?pathos=abc_top&file=2023_05_11_07

# http://127.0.0.1:5000/get_archives?pathos=abc_top&file=latest


# http://127.0.0.1:5000/check_archives?folder=abc_top

# https://thambili.herokuapp.com/get_data?file=latest_foi

# http://127.0.0.1:5000/get_data?file=latest_foi

