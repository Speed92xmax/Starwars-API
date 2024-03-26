"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import json
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Characters,Planets,Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
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
"""--------- USERS LIST --------- """
@app.route('/user', methods=['GET'])
def get_users():
    users= User.query.all()
    
    if len(users) < 1 :
        return jsonify({
            'msg':'not found'
        }),404
        
    serialize = list(map(lambda x: x.serialize(),users))
    return serialize,200

"""--------- CREATE USER --------- """

@app.route('/user', methods=['POST'])
def create_one_user():
    body = request.json
    name = body.get('name',None),
    email = body.get('email',None),
    password = body.get('password',None),
    new_user = User(
        name=name,
        email=email,
        password=password,
        is_active = True
    )
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({"msg": "user created successful"}), 201
    except Exception as error:
        print('------------Error:',error),
        db.session.rollback()
        return jsonify({'ok':False,'error': 'internal server error','status':500}),500



"""--------- USER FAVORITE LIST--------- """

@app.route('/user/favorite/<int:id>', methods=["GET"])
def get_favorite(id):
    """ Agregar verificación de existencia de usuario"""
    favorites = Favorites.query.filter(Favorites.user_id == id).all()
    if not favorites:
        return jsonify({'ok': False, 'error': 'No favorites found for the user'}), 404
    serialized_favorites = [favorite.serialize() for favorite in favorites]
    return jsonify({'ok': True, 'data': serialized_favorites}),200



"""--------- ADD PLANET TO FAVORITE --------- """

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_to_favorite(planet_id):
        body=request.json
        user_id=body.get('user_id', None)
        resp = User.query.filter_by(id = user_id).one_or_none()
        if resp is None:
            return 'user is not fount'
        resp = Planets.query.filter_by(id = planet_id).one_or_none()
        if resp is None:
            return 'planet is not found'
        new_favorite=Favorites(user_id=user_id, planets_id=planet_id)
        db.session.add(new_favorite)
        try:
            db.session.commit()
            return 'Favorite created'
        except Exception as error:
            db.session.rollback()
            print("-*-*-*- Error encontrado: ", error)
            return 'an error ocurred'


"""--------- ADD CHARACTER TO FAVORITE --------- """

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_character_to_favorite(character_id):
        body=request.json
        user_id=body.get('user_id', None)
        
        resp = User.query.filter_by(id = user_id).one_or_none()
        if resp is None:
            return 'user is not fount'
        
        resp = Characters.query.filter_by(id = character_id).one_or_none()
        if resp is None:
            return 'character is not found'
        
        new_favorite=Favorites(user_id=user_id, characters_id=character_id)
        db.session.add(new_favorite)
        try:
            db.session.commit()
            return 'Favorite created'
        except Exception as error:
            db.session.rollback()
            print("-*-*-*- Error encontrado: ", error)
            return 'an error ocurred'

"""--------- DELETE CHARACTER TO FAVORITE --------- """

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_character_from_favorite(character_id):
        body=request.json
        user_id=body.get('user_id', None)
        resp = User.query.filter_by(id = user_id).one_or_none()
        if resp is None:
            return 'user is not found'
       
        resp = Favorites.query.filter_by(user_id = user_id, character_id = character_id).all()
        if not resp:
            return 'character is not found',404

        for element in resp:
            db.session.delete(element)

        try:
            db.session.commit()
            return 'Favorite DELETED',200
        except Exception as error:
            db.session.rollback()
            print('\\\ Error encontrado: /// ', error)
            return 'an error ocurred',404
        
"""--------- DELETE PLANET TO FAVORITE --------- """

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_from_favorite(planet_id):
        body=request.json
        user_id=body.get('user_id', None)
        resp = User.query.filter_by(id = user_id).one_or_none()
        if resp is None:
            return 'user is not found'
       
        resp = Favorites.query.filter_by(user_id = user_id, planet_id = planet_id).all()
        if not resp:
            return 'planet is not found',404

        for element in resp:
            db.session.delete(element)

        try:
            db.session.commit()
            return 'Favorite DELETED',200
        except Exception as error:
            db.session.rollback()
            print('\\\ Error encontrado: /// ', error)
            return 'an error ocurred',404

"""--------- CHARACTERS LIST --------- """
@app.route('/characters', methods=['GET'])
def get_characters():
    characters= Characters.query.all()
    
    if len(characters) < 1 :
        return jsonify({
            'msg':'not found'
        }),404
        
    serialize = list(map(lambda x: x.serialize(),characters))
    return serialize,200
   
"""--------- CHARACTER ELEMENT --------- """
@app.route('/character/<int:id>',methods=['GET'])
def get_character(id):
    character = Characters.query.filter_by(id=id).one_or_none()
    if character is None:
        return jsonify({'ok':False,'error':'character not found ','status':404}),404

    return jsonify({'ok':True,'data':character.serialize()})

"""--------- PLANETS LIST --------- """
@app.route('/planets', methods=['GET'])
def get_planets():
    planets= Planets.query.all()
    
    if len(planets) < 1 :
        return jsonify({
            'msg':'not found'
        }),404
        
    serialize = list(map(lambda x: x.serialize(),planets))
    return serialize,200
   
"""--------- PLANET ELEMENT --------- """

@app.route('/planet/<int:id>',methods=['GET'])
def get_planet(id):
    planet = Planets.query.filter_by(id=id).one_or_none()
    if planet is None:
        return jsonify({'ok':False,'error':'planet not found ','status':404}),404

    return jsonify({'ok':True,'data':planet.serialize()})



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
