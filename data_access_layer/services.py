"""
All logic and DB operations placed here.

Import as:
import data_access_layer.services as services
"""
from typing import Type

from marshmallow import ValidationError
from marshmallow import Schema
from sqlalchemy import MetaData
from sqlalchemy.sql.expression import ClauseElement

import api.app as app
import data_access_layer.model.cast as cast
import data_access_layer.model.genre as genre
import data_access_layer.model.movie as movie
import data_access_layer.schemas as schemas


session = app.db.session


def validate_movie(movie_schema: Type[Schema], data: dict):
    try:
        movie_schema().load(data)
        return True
    except ValidationError as err:
        print(err.messages)
        print(err.valid_data)
        return False


def create_movie(data: dict):
    if validate_movie(schemas.MovieCreateSchema, data):
        create_movie_from_dict(data)


def update_movie(movie_id: int, data: dict):
    if check_movie_exists(movie_id) and validate_movie(schemas.MovieUpdateSchema, data):
        update_movie_from_dict(movie_id, data)


def delete_movie(movie_id: int):
    session.commit()
    with session.begin():
        delete_cast_genres_from_movie(movie_id)
        db_movie = session.get(movie.Movie, movie_id)
        if db_movie:
            session.delete(db_movie)
    session.commit()


def get_or_create(model, defaults=None, is_commit=False, **kwargs):
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
            if is_commit:
                session.commit()
        except Exception:
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance
        else:
            return instance


def create_bulk_movie_from_dict(json_movie: dict) -> None:
    # TODO(*): Find out why PyCharm warn: Unexpected arguments in the SQLAlchemy models constructors
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


def create_movie_from_dict(json_movie: dict) -> None:
    db_movie = movie.Movie(
        title=json_movie['title'],
        year=json_movie['year'])
    session.add(db_movie)
    session.commit()
    for actor_id in json_movie["cast"]:
        session.add(cast.ActorMovie(actor_id=actor_id, movie_id=db_movie.id))
    for genre_id in json_movie["genres"]:
        session.add(genre.GenreMovie(genre_id=genre_id, movie_id=db_movie.id))
    session.commit()


def update_movie_from_dict(movie_id, json_movie: dict) -> None:
    session.commit()
    with session.begin():
        db_movie = session.query(movie.Movie).get(movie_id)
        db_movie.update(**json_movie)
        delete_cast_genres_from_movie(movie_id)
        for actor_id in json_movie["cast"]:
            session.add(get_or_create(cast.ActorMovie, movie_id=movie_id, actor_id=actor_id))
        for genre_id in json_movie["genres"]:
            session.add(get_or_create(genre.GenreMovie, movie_id=movie_id, genre_id=genre_id))
    session.commit()


def delete_cast_genres_from_movie(movie_id: int) -> None:
    session.query(genre.GenreMovie).filter_by(movie_id=movie_id).delete()
    session.query(cast.ActorMovie).filter_by(movie_id=movie_id).delete()


def check_movie_exists(movie_id: int) -> bool:
    return session.query(movie.Movie).get(movie_id) is not None


def kill_em_all() -> None:
    """Delete all the data from the database"""
    metadata = MetaData()
    metadata.reflect(bind=app.engine)

    for table in reversed(metadata.sorted_tables):
        session.execute(table.delete())
