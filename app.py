# app.py
import os
import json
import threading
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from vision_rescue import runcameracheck

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    try:
        with open("reports.json") as f:
            reports = [json.loads(line) for line in f]
    except FileNotFoundError:
        reports = []
    return render_template("index.html", reports=reports)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded", "status": "error"})
    file = request.files["file"]
    name = request.form.get("name")
    location = request.form.get("location")

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"message": "Invalid or no file", "status": "error"})

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    report = {
        "filename": filename,
        "name": name,
        "location": location,
        "status": "missing"
    }

    with open("reports.json", "a") as f:
        f.write(json.dumps(report) + "\n")

    return jsonify({"message": "File uploaded successfully", "status": "success"})

@app.route("/start_verification")
def start_verification():
    threading.Thread(target=runcameracheck).start()
    return "Camera verification started"

if __name__ == "__main__":
    app.run(debug=True)
