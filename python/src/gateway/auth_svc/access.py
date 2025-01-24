import os
import requests
from flask import jsonify


def login(request):
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"error": "Missing credentials"}), 401

    payload = {"email": auth.username, "password": auth.password}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
            json=payload,
            headers=headers,
        )
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, (response.json(), response.status_code)
    except requests.exceptions.RequestException:
        return (
            jsonify({"error": "Failed to connect to the authentication service"}),
            500,
        )
