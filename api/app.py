"""
The main Flask application

Import as:
import api.app as app
"""

from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data_access_layer/db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
engine = db.get_engine()

# TODO(*): Split it to the separate modules.
import data_access_layer.services as services # noqa


class MovieCreate(Resource):
    def post(self):
        created_movie = services.create_movie(request.json)
        return {"message": "The movie successfully created.",
                "result": created_movie}


class MovieUpdateDelete(Resource):
    def put(self, movie_id: int):
        updated_movie = services.update_movie(movie_id, request.json)
        if not updated_movie:
            abort(404)
        return {"message": "The movie successfully updated.",
                "result": updated_movie}

    def delete(self, movie_id: int):
        deleted_movie = services.delete_movie(movie_id)
        if not deleted_movie:
            abort(404)
        return {"message": "The movie successfully deleted.",
                "result": deleted_movie}


class Report(Resource):
    def get(self):
        return services.get_amount_of_movies_by_actor_and_year()


api.add_resource(MovieCreate, '/movie')
api.add_resource(MovieUpdateDelete, '/movie/<int:movie_id>')
api.add_resource(Report, '/report')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
