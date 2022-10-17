"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# INSERT NEW USER
@app.route('/user', methods=['POST'])
def create_user():
    request_body = request.get_json(force=True)
    request_keys = list(request_body.keys())
    if len(request_keys)==0:
        return "The request body is null", 400
    elif 'email' not in request_keys or request_body['email']=="":
        return 'You need to specify the email', 400
    elif 'password' not in request_keys or request_body['password']=="":
        return 'You need to specify the password', 400
    elif User.query.filter_by(email = request_body['email']).first() != None:
        return 'This email is already in use',500
    else:
        email = request_body['email']
        password = request_body['password']

        new_user = User(email,password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize()), 200

# GET ALL USERS
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()

    if len(users) == 0:
        return jsonify({"msg":"No users found"}),500
    else:
        output = []

        for user in users:
            user_data = {}
            user_data['id'] = habit.id
            user_data['email'] = habit.email
            user_data['username'] = habit.username
            output.append(user_data)

        return jsonify({'users': output})

# INSERT NEW CHARACTER
@app.route('/people', methods=['POST'])
def create_char():
    request_body = request.get_json(force=True)
    try:
        check = Character.query.filter_by(name=request_body["name"]).first()
        if check != None:
            raise Exception()
    except Exception:
        return jsonify({"msg":f"This character already exists in the database:{check.serialize()}"}),500
    else:
        character = Character()
        fields = list(character.serialize().keys())
        fields.remove("id")
    if all(f in request_body for f in fields):
        if all(value != "" for value in request_body.values()):
            new_character = Character()
            for f in fields:
                setattr(new_character, f, request_body[f])
            db.session.add(new_character)
            db.session.commit()
            return jsonify(new_character.serialize()),200
        else:
            missing_values = []
            for f in fields:
                if request_body[f] == "": 
                    missing_values.append(f)
            return jsonify(f"The following field values are empty: {missing_values}"),400
    else:
        missing_fields = []
        for f in fields:
            if f not in request_body: 
                missing_fields.append(f)
        return jsonify(f"The following fields are missing: {missing_fields}"),400

# UPDATE CHARACTER
@app.route('/people/<int:id>', methods=['PUT'])
def update_char(id):
    character = Character.query.filter_by(id=id).first()
    if character != None:
        request_body = request.get_json(force=True)
        fields = list(character.serialize().keys())
        fields.remove("id")
        unvalid_fields = []
        for f in request_body:
            if f in fields:
                if f == id:
                    return jsonify({"msg":"You cant modify id"}),400
                else:
                    setattr(character, f, request_body[f])
            else:
                unvalid_fields.append(f)
        if len(unvalid_fields)>0:
            return jsonify({"msg":f"These fields are not valid: {unvalid_fields}"}),400
        else:
            return jsonify(character.serialize()),200
    else:
        return jsonify({"msg":"This character doesnt exist"}),500


# DELETE CHARACTER
@app.route('/people/<int:id>', methods=['DELETE'])
def delete_char(id):
    try:
        character = Character.query.filter_by(id=id).first()
        if character == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"This character doesnt exist"}),500
    else:
        db.session.delete(character)
        db.session.commit()
        return jsonify(character.serialize()),200

# GET ALL CHARACTERS
@app.route('/people', methods=['GET'])
def get_people():
    all_people = Character.query.all()
    all_people = list(map(lambda x: x.serialize(), all_people))
    json_text = jsonify(all_people)
    return json_text

# GET CHARACTER
@app.route('/people/<int:character_id>', methods=['GET'])
def get_character(character_id):
    try:
        char = Character.query.get(character_id)
        if char == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"That character doesnt exist in the database"}),400
    else:
        return jsonify(char.serialize()), 200

# INSERT A NEW PLANET
@app.route('/planet', methods=['POST'])
def create_planet():
    request_body = request.get_json(force=True)
    fields = ["name", "climate", "population", "orbital_period", "rotation_period", "diameter"]
    try:
        check = Planet.query.filter_by(name=request_body["name"]).first()
        if check != None:
            raise Exception()
    except Exception:
        return jsonify({"msg":f"This planet already exists in the database:{check.serialize()}"}),500
    else:
        planet = Planet()
        fields = list(planet.serialize().keys())
        fields.remove("id")
    if all(f in request_body for f in fields):
        if all(value != "" for value in request_body.values()):
            new_planet = Planet()
            for f in fields:
                setattr(new_planet, f, request_body[f])
            db.session.add(new_planet)
            db.session.commit()
            return jsonify(new_planet.serialize()),200
        else:
            missing_values = []
            for f in fields:
                if request_body[f] == "": 
                    missing_values.append(f)
            return jsonify(f"The following field values are empty: {missing_values}"),400
    else:
        missing_fields = []
        for f in fields:
            if f not in request_body: 
                missing_fields.append(f)
        return jsonify(f"The following fields are missing: {missing_fields}"),400

# UPDATE PLANET
@app.route('/planet/<int:id>', methods=['PUT'])
def update_planet(id):
    planet = Planet.query.filter_by(id=id).first()
    if planet != None:
        request_body = request.get_json(force=True)
        fields = list(planet.serialize().keys())
        fields.remove("id")
        unvalid_fields = []
        for f in request_body:
            if f in fields:
                if f == id:
                    return jsonify({"msg":"You cant modify id"}),400
                else:
                    setattr(planet, f, request_body[f])
            else:
                unvalid_fields.append(f)
        if len(unvalid_fields)>0:
            return jsonify({"msg":f"These fields are not valid: {unvalid_fields}"}),400
        else:
            return jsonify(planet.serialize()),200
    else:
        return jsonify({"msg":"This planet doesnt exist"}),500

# DELETE PLANET
@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
    try:
        planet = Planet.query.filter_by(id=id).first()
        if planet == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"This planet doesnt exist"}),500
    else:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(planet.serialize()),200

# GET ALL PLANETS
@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), all_planets))
    json_text = jsonify(all_planets)
    return json_text, 200

# GET A SINGLE PLANET INFORMATION
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    try:
        planet = Planet.query.get(planet_id)
        if planet == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"That planet doesnt exist in the database"}),400
    else:
        return jsonify(planet.serialize()), 200

#Get all the favorites that belong to the current user.
@app.route('/users/favourites', methods=['GET'])
def get_favourites():
    active_user = User.query.filter_by(is_active=True).first()
    try:
        if active_user == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"No user is active"}),500
    else:
        favourites = Favourite.query.filter_by(user_id=active_user.id)
        favourites = list(map(lambda x: x.serialize(), favourites))

        return jsonify(favourites),200

#Add a new favourite planet to the current user
@app.route('/favourite/planet/<int:planet_id>', methods=['POST'])
def add_favourite_planet(planet_id):
    active_user = User.query.filter_by(is_active=True).first()
    checkFav = Favourite.query.filter_by(user_id=active_user.id, planet_id=planet_id).first()

    try:
        checkPlanet = Planet.query.get(planet_id)
        if checkPlanet == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The planet doesnt exist in the database"}),400

    try:
        new_favourite_planet = Favourite(user_id=active_user.id, planet_id=planet_id)
        if checkFav != None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"The user already has this planet as favourite"}),500
    else:
        db.session.add(new_favourite_planet)
        db.session.commit()
        return jsonify(new_favourite_planet.serialize()),200

#Add a new favourite character to the current user
@app.route('/favourite/people/<int:character_id>', methods=['POST'])
def add_favourite_character(character_id):

    active_user = User.query.filter_by(is_active=True).first()
    checkFav = Favourite.query.filter_by(user_id=active_user.id, character_id=character_id).first()
    try:
        checkChar = Character.query.get(character_id)
        if checkChar == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The character doesnt exist in the database"}),400

    try:
        new_favourite_character = Favourite(user_id=active_user.id, character_id=character_id)
        if checkFav != None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"The user already has this character as favourite"}),500
    else:
        db.session.add(new_favourite_character)
        db.session.commit()
        return jsonify(new_favourite_character.serialize()),200

# DELETE FAVOURITE PLANET
@app.route('/favourite/planet/<int:planet_id>', methods = ['DELETE'])
def delete_favourite_planet(planet_id):
    active_user = User.query.filter_by(is_active=True).first()
    try:
        checkPlanet = Planet.query.get(planet_id)
        if checkPlanet == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The planet doesnt exist in the database"}),400
    try:
        user_fav_planet = Favourite.query.filter_by(user_id=active_user.id, planet_id=planet_id).first()
        if user_fav_planet == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"This user doesnt have this planet as favourite"}),500
    else:
        db.session.delete(user_fav_planet)
        db.session.commit()
        return jsonify(user_fav_planet.serialize()),200

# DELETE FAVOURITE CHARACTER
@app.route('/favourite/people/<int:character_id>', methods = ['DELETE'])
def delete_favourite_character(character_id):
    active_user = User.query.filter_by(is_active=True).first()
    try:
        checkChar = Character.query.get(character_id)
        if checkChar == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The character doesnt exist in the database"}),400

    try:
        user_fav_character = Favourite.query.filter_by(user_id=active_user.id, character_id=character_id).first()
        if user_fav_character == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"This user doesnt have this character as favourite"}),500
    else:
        db.session.delete(user_fav_character)
        db.session.commit()
        return jsonify(user_fav_character.serialize()),200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
