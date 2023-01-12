# flask api example
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from recorder import Recorder
recorder = Recorder("xfghvlkjszncfhegvlszjcfhgoild")
app = Flask(__name__)
api = Api(app)

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(recorder.get_status())

@app.route("/api/controls/start", methods=["POST"])
def start():
    recorder.start_recording()
    return jsonify({"status":"started"})

@app.route("/api/controls/stop", methods=["POST"])
def stop():
    recorder.end_recording()
    return jsonify({"status":"stopped"})

@app.route("/api/controls/pause", methods=["POST"])
def pause():
    recorder.paused = True
    return jsonify({"status":"paused"})

@app.route("/api/controls/resume", methods=["POST"])
def resume():
    recorder.paused = False
    return jsonify({"status":"resumed"})


app.run()