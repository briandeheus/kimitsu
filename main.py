import os
import time
import uuid
import subprocess

import dotenv
from flask import Flask, jsonify, Response, request, render_template

dotenv.load_dotenv()
app = Flask(__name__)

BASE_PATH = os.environ["BASE_PATH"]


def get_key_ids_from_output(output):
    key_ids = []
    for data in output.decode().split("\n"):
        if "keyid" not in data:
            continue
        key_ids.append(data.split(" ")[-1])
    return key_ids


def get_key_ids(secret_id):
    parse_key = subprocess.run(
        ["gpg", "--list-packets", get_key_dir(secret_id)], capture_output=True
    )

    if parse_key.returncode != 0:
        return []

    return get_key_ids_from_output(parse_key.stdout)


def get_secret_dir(secret_id):
    return os.path.join(BASE_PATH, "secrets", secret_id)


def get_key_dir(secret_id):
    return os.path.join(BASE_PATH, "keys", secret_id)


def secret_exists(secret_id):
    return os.path.isfile(get_secret_dir(secret_id))


def key_exists(secret_id):
    return os.path.isfile(get_key_dir(secret_id))


@app.route("/api/secrets", methods=["post"])
def create_secret():
    try:
        key_bytes = request.get_data()
    except Exception:
        res = jsonify({"error": "This does not look like a PGP/GPG public key to me."})
        res.status = 400
        return res

    load_key = subprocess.Popen(
        ["echo", key_bytes.decode()], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    parse_key = subprocess.run(
        ["gpg", "--list-packets"], stdin=load_key.stdout, capture_output=True
    )

    if parse_key.returncode != 0:
        res = jsonify({"error": parse_key.stderr.decode().strip()})
        res.status = 400
        return res

    secret_id = uuid.uuid4().hex
    secret_id = "{:x}{}".format(int(time.time()), secret_id)

    with open(os.path.join(BASE_PATH, "keys", secret_id), "wb") as f:
        f.write(key_bytes)

    res = jsonify({"secret_id": secret_id})
    res.status = 400
    return res


@app.route("/api/secrets/<secret_id>", methods=["put"])
def store_secret(secret_id):
    if not key_exists(secret_id):
        res = jsonify({"error": "key could not be found"})
        res.status = 404
        return res

    if secret_exists(secret_id):
        res = jsonify({"error": "this secret has already been created"})
        res.status = 400
        return res

    encrypted = request.get_data()
    load_encrypted = subprocess.Popen(
        ["echo", encrypted.decode()], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    parse_key = subprocess.run(
        ["gpg", "--pinentry-mode", "cancel", "--list-packets"], stdin=load_encrypted.stdout, capture_output=True
    )

    target_key_ids = get_key_ids(secret_id)
    signed_key_ids = get_key_ids_from_output(parse_key.stdout)
    valid_key = False

    for key in signed_key_ids:
        if key in target_key_ids:
            valid_key = True
            break

    if not valid_key:
        res = jsonify({"error": "this secret seems to be encrypted with the wrong key."})
        res.status = 400
        return res

    with open(get_secret_dir(secret_id), "wb") as file:
        file.write(encrypted)

    res = Response()
    res.status_code = 201

    return res


@app.route("/api/secrets/<secret_id>", methods=["get"])
def retrieve_secret(secret_id):
    if not secret_exists(secret_id):
        res = Response()
        res.status = 404
        return res

    res = Response()
    res.content_type = "application/x-pem-file"
    with open(get_secret_dir(secret_id=secret_id), "rb") as file:
        res.data = file.read()

    return res


@app.route("/api/keys/<secret_id>.asc", methods=["get"])
def retrieve_key(secret_id):
    if not key_exists(secret_id):
        res = Response()
        res.status = 404
        return res

    with open(os.path.join(BASE_PATH, "keys", secret_id), "rb") as f:
        res = Response(f.read())
        res.content_type = "application/x-pem-file"
        return res


@app.route("/secrets/<secret_id>", methods=["get"])
def secret_view(secret_id):
    if not key_exists(secret_id) or secret_exists(secret_id):
        res = Response()
        res.data = "Not found."
        res.status = 404
        return render_template("404.html"), 404

    return render_template("secret.html")


@app.route("/", methods=["get"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run()
