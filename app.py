from flask import Flask, request, send_file, redirect
import os 
import io
import csv

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"


@app.route('/get_data')
def get_csv():
    """ 
    Returns the csv file requested.
    """
    # Checking that the month parameter has been supplied
    if not "file" in request.args:
        return "You haven't specificed a file"
    # Also make sure that the value provided is numeric
    try:
        month = int(request.args["file"])
    except:
        return "You haven't specificed a file that exists"
    
    csv_path = f"static/{month}.csv"   

    # Also make sure the requested csv file does exist
    if not os.path.isfile(csv_path):
        return f"ERROR: file {month} was not found on the server"
    # Send the file back to the client
    return send_file(csv_path, as_attachment=True, attachment_filename=f'{month}.csv')


https://thambili.herokuapp.com/get_data/file=latest_foi