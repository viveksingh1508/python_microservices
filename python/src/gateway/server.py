import gridfs
import pika
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
import json


server = Flask(__name__)

server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    response = access.login(request)
    return response


@server.route("/upload", methods=["POST"])
def upload():
    access_token, err = validate.token(request)
    access_data = json.loads(access_token)
    if access_data["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return jsonify({"message": "exactly 1 file required"}), 400

        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access_data)

            if err:
                return jsonify({"error": err})

        return ({"message": "file uploaded successfully"}), 200

    else:
        return ({"error": "not authorized"}), 401


@server.route("/download", methods=["GET"])
def download():
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5001, debug=True)
