# flask api example
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import tray
import recorder

INDEX_PATH = r"frontend\public"
# this path contains index.html and all the other frontend files
app = Flask(__name__)
api = Api(app)

#serve index.html at the root
@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/status")
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
