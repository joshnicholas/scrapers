from flask import Flask, request, send_file, redirect, Response, jsonify
import os 
import io
import csv
import pandas as pd 

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"


@app.route('/get_data', methods=["GET"])
def get_csv():
    """ 
    Returns the csv file requested.
    """
    # Checking that the month parameter has been supplied
    if not "file" in request.args:
        return "You haven't specificed a file"

    month = request.args["file"]

    stem = month.split(".")[-0]
    
    csv_path = f"./static/{month}.csv"   

    # csv_path = 'static/latest_foi.csv'

    inter = pd.read_csv(csv_path)

    jsony = inter.to_json(orient='records')

    return jsonify(jsony)



    # print(month)

    # # Also make sure the requested csv file does exist
    # if not os.path.isfile(csv_path):
    #     return f"ERROR: file {month} was not found on the server"
    # # Send the file back to the client
    # return send_file(csv_path, as_attachment=True)


# https://thambili.herokuapp.com/get_data?file=latest_foi

# http://127.0.0.1:5000/get_data?file=latest_foi

