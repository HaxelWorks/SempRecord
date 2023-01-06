# flask api example
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from recorder import recorder
app = Flask(__name__)
api = Api(app)

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(recorder.get_status())




# @app.route('/<int:number>/')
# def incrementer(number):
#     return "Incremented number is " + str(number+1)

# @app.route('/<string:name>/')
# def hello(name):
#     return "Hello " + name

app.run()