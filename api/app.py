"""
The main Flask application

Import as:
import api.app as app
"""

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

import data_access_layer.services as services

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data_access_layer/db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
engine = db.get_engine()


class MovieCreate(Resource):
    def post(self):
        services.create_movie(request.json)
        return {'hello': 'world'}


api.add_resource(MovieCreate, '/movie')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
