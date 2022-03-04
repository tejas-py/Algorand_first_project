from flask import Flask, jsonify

app = Flask(__name__)


family = {'name2': 'Muskan', 'age2': '22', 'home' : 'gzb'}


@app.route('/')
def index():
    return "<p>Welcome to the homepage.</p>"


@app.route('/sum/<int:a>')
def add(a):
    x = a+5
    dic = {"a":1}

    return dic


@app.route('/family', methods=['GET'])
def get():
    return jsonify({'family': family})


@app.route('/families', methods=['POST'])
def create():
    families = {'name': 'Deepak', 'age': '50'}
    family.append(families)
    return jsonify({'Created': families})


@app.route('/family/<int:age>', methods=['GET'])
def get_age(age):
    return jsonify({'family': family[age]})


@app.route('/families/<string:name>', methods=['PUT'])
def family_update(name):
    newfamily = {'name2': name}
    family.update(newfamily)
    return jsonify({'families': family})


if __name__ == '__main__':
    app.run(debug=True)
