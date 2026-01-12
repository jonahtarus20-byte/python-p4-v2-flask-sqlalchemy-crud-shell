# server/app.py

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Pet

# create a Flask application instance
app = Flask(__name__)

# configure the database connection to the local file app.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# configure flag to disable modification tracking and use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a Migrate object to manage schema modifications
migrate = Migrate(app, db)

# initialize the Flask application to use the database
db.init_app(app)

# Routes

@app.route('/pets', methods=['GET'])
def pets():
    pets = Pet.query.all()
    pets_dict = [pet.to_dict() for pet in pets]
    return make_response(jsonify(pets_dict), 200)

@app.route('/pets/<int:id>', methods=['GET'])
def pet_by_id(id):
    pet = Pet.query.filter_by(id=id).first()
    if pet:
        return make_response(jsonify(pet.to_dict()), 200)
    else:
        return make_response(jsonify({"error": "Pet not found"}), 404)

@app.route('/pets', methods=['POST'])
def create_pet():
    data = request.get_json()
    name = data.get('name')
    species = data.get('species')

    if not name or not species:
        return make_response(jsonify({"error": "Name and species are required"}), 400)

    new_pet = Pet(name=name, species=species)
    db.session.add(new_pet)
    db.session.commit()

    return make_response(jsonify(new_pet.to_dict()), 201)

@app.route('/pets/<int:id>', methods=['PATCH'])
def update_pet(id):
    pet = Pet.query.filter_by(id=id).first()
    if not pet:
        return make_response(jsonify({"error": "Pet not found"}), 404)

    data = request.get_json()
    if 'name' in data:
        pet.name = data['name']
    if 'species' in data:
        pet.species = data['species']

    db.session.commit()
    return make_response(jsonify(pet.to_dict()), 200)

@app.route('/pets/<int:id>', methods=['DELETE'])
def delete_pet(id):
    pet = Pet.query.filter_by(id=id).first()
    if not pet:
        return make_response(jsonify({"error": "Pet not found"}), 404)

    db.session.delete(pet)
    db.session.commit()
    return make_response(jsonify({"message": "Pet deleted"}), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
