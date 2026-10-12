from flask import Flask, render_template, make_response, jsonify
from lab.io_utils import load_students
import os

app = Flask(__name__, static_folder="static", template_folder="static")


DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "students.csv")


@app.route("/", methods=["GET"])
def index():
    students = load_students(DATA_PATH)
    
    
    response = make_response(render_template("index.html", students=students))
    
    
    response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400, must-revalidate"
    return response


@app.route("/api/data", methods=["GET"])
def get_data():
    
    students = load_students(DATA_PATH)
    response = jsonify([s.to_dict() for s in students])
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=3600"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)