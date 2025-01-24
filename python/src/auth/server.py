import jwt
import datetime
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:vivek@localhost/postgres"
)
server.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:vivek@localhost/postgres"
)
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(server)
migrate = Migrate(server, db)


# def get_db_connection():
#     conn = psycopg2.connect(
#         host="localhost",
#         database="postgres",
#         user=os.environ["DB_USERNAME"],
#         password=os.environ["DB_PASSWORD"],
#     )
#     return conn

# @server.route("/")
# def index():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM employee;")
#     employee = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify({"employee": employee})


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


@server.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    if not auth or not auth.get("email") or not auth.get("password"):
        return jsonify({"error": "Missing credentials"}), 401

    user = User.query.filter_by(email=auth.get("email")).first()
    if user and check_password_hash(user.password, auth.get("password")):
        return createJWT(auth.get("email"), os.environ.get("JWT_SECRET"), True)
    else:
        return jsonify({"error": "Invalid credentials"}), 401


def createJWT(username, secret, authz):
    return jsonify(
        {
            "message": jwt.encode(
                {
                    "username": username,
                    "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                    + datetime.timedelta(days=1),
                    "iat": datetime.datetime.now(tz=datetime.timezone.utc),
                    "admin": authz,
                },
                secret,
                algorithm="HS256",
            )
        }
    )


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return jsonify({"error": "missing credentials"}), 401
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
        return jsonify({"message": decoded}), 200
    except Exception:
        return jsonify({"error": "not authorized"}), 403


@server.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    hashed_password = generate_password_hash(password)
    user = User(email=email, password=hashed_password)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "User already exists"}), 409


if __name__ == "__main__":
    server.run(debug=True, host="0.0.0.0", port=5000)
