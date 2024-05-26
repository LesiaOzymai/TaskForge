from flask import Flask
from flask import request, jsonify
from module import Project

app = Flask(__name__)
project = Project()

@app.route("/project/all", methods=["GET"])
def get_all_projects():
    result =project.get_all_projects()
    return jsonify(result), 200

@app.route("/project/<id>", methods=["GET"])
def get_project(id):
    result =project.get_project(id)
    return jsonify(result), 200

@app.route("/project/add", methods=["POST"])
def add_project():
    data = request.get_json()
    result =project.add_project(data)
    return jsonify(result), 200

@app.route("/project/update", methods=["PATCH"])
def update_project():
    data = request.get_json()
    result =project.update_project(data)
    return jsonify(result), 200

@app.route("/project/delete/<id>", methods=["DELETE"])
def delete_project(id):
    result =project.delete_project(id)
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)