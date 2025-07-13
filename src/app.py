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
from models import db, User, People, Planet
# from models import Person

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

@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_all_people():
    people_list = People.query.all()
    results = [person.serialize() for person in people_list]
    return jsonify(results), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"message": "Person not found"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    return jsonify(results), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    results = [user.serialize() for user in users]
    return jsonify(results), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    try:
        print("🔍 Endpoint /users/favorites ha sido llamado")

        user = User.query.get(1)
        if not user:
            print("❌ Usuario con ID 1 no encontrado")
            return jsonify({"message": "User not found"}), 404

        print("✅ Usuario encontrado:", user.serialize())

        favorite_people = People.query.limit(2).all()
        print("👤 Personas favoritas encontradas:", [p.name for p in favorite_people])

        favorite_planets = Planet.query.limit(2).all()
        print("🪐 Planetas favoritas encontradas:", [p.name for p in favorite_planets])

        return jsonify({
            "user_id": user.id,
            "people": [p.serialize() for p in favorite_people],
            "planets": [p.serialize() for p in favorite_planets]
        }), 200

    except Exception as e:
        print("🔥 ERROR atrapado en except:", str(e))
        return jsonify({"error": str(e)}), 500


# this only runs if `$ python src/app.py` is executed
print("🚀 Flask app is running and endpoints are loaded.")
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
