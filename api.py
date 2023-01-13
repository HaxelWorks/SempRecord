# flask api example
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import tray
import recorder
app = Flask(__name__)
api = Api(app)


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(recorder.RECORDER.get_status())


@app.route("/api/controls/start", methods=["POST"])
def start():
    tray.start()
    return jsonify({"status": "started"})


@app.route("/api/controls/stop", methods=["POST"])
def stop():
    tray.stop()
    return jsonify({"status": "stopped"})


@app.route("/api/controls/pause", methods=["POST"])
def pause():
    tray.pause()
    return jsonify({"status": "paused"})


@app.route("/api/controls/resume", methods=["POST"])
def resume():
    tray.start()
    return jsonify({"status": "resumed"})


app.run()
