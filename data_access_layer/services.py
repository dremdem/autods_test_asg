"""
All logic and DB operations placed here.

Import as:
import data_access_layer.services as services
"""

import datetime as dt

from marshmallow import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import ClauseElement

import api.app as app
import data_access_layer.model.cast as cast
import data_access_layer.model.genre as genre
import data_access_layer.model.movie as movie
import data_access_layer.schemas as schemas

session = app.db.session


def validate_movie(data: dict):
    try:
        schemas.MovieCreateSchema().load(data)
        return True
    except ValidationError as err:
        print(err.messages)
        print(err.valid_data)
        return False


def create_movie(data: dict):
    validate_movie(data)


def get_or_create(model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance
    else:
        params = {k: v for k, v in kwargs.items()
                  if not isinstance(v, ClauseElement)}
        params.update(defaults or {})
        instance = model(**params)
        try:
            session.add(instance)
            session.commit()
        except Exception:
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance
        else:
            return instance


def create_movie_from_dict(json_movie: dict) -> movie.Movie:
    db_movie = movie.Movie(
        title=json_movie['title'],
        year=json_movie['year'])
    session.add(db_movie)
    casts = list(map(lambda x: get_or_create(cast.Actor, name=x),
                             json_movie['cast']))
    genres = list(map(lambda x: get_or_create(genre.Genre, name=x),
                               json_movie['genres']))
    for db_actor in casts:
        session.add(cast.ActorMovie(actor_id=db_actor.id, movie_id=db_movie.id))
    for db_genre in genres:
        session.add(genre.GenreMovie(genre_id=db_genre.id, movie_id=db_movie.id))
    session.commit()


