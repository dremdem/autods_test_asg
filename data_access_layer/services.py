"""
All logic and DB operations placed here.

Import as:
import data_access_layer.services as services
"""
from typing import Type, List

from marshmallow import ValidationError
from marshmallow import Schema
from sqlalchemy import MetaData, func
from sqlalchemy.sql.expression import ClauseElement

import api.app as app
import data_access_layer.model.cast as cast
import data_access_layer.model.genre as genre
import data_access_layer.model.movie as movie
import data_access_layer.schemas as schemas
from model.base import Base


session = app.db.session


def validate_movie(movie_schema: Type[Schema], data: dict) -> bool:
    """
    Validator for the data for any schema.

    :param movie_schema: Schema what will be validate.
    :param data: Data dict that have to be validated.
    :return: Result of a validation.
    """
    try:
        movie_schema().load(data)
        return True
    except ValidationError as err:
        # TODO(*): Rework as logging
        print(err.messages)
        print(err.valid_data)
        return False


def create_movie(data: dict) -> dict:
    """
    Create a movie with a dict data.

    :param data: Dict with a movie data including IDs of the cast and genres.
    :return: Dict with the movie data with the new ID.
    """
    if validate_movie(schemas.MovieCreateSchema, data):
        db_movie = create_movie_from_dict(data)
        return schemas.MovieReturnSchema().dump(db_movie)


def update_movie(movie_id: int, data: dict):
    """
    Update a movie with a dict data.

    :param movie_id: ID of the DB movie.
    :param data: Dict with a movie data including IDs of the cast and genres.
    :return: Dict with the movie data with the ID.
    """
    if check_movie_exists(movie_id) and validate_movie(schemas.MovieUpdateSchema, data):
        db_movie = update_movie_from_dict(movie_id, data)
        return schemas.MovieReturnSchema().dump(db_movie)


def delete_movie(movie_id: int):
    """
    Delete a movie by ID.

    :param movie_id: ID of the DB movie.
    :return: Dict with the deleted movie data with the ID.
    """
    session.commit()
    with session.begin():
        delete_cast_genres_from_movie(movie_id)
        db_movie = session.get(movie.Movie, movie_id)
        json_movie = schemas.MovieReturnSchema().dump(db_movie)
        if db_movie:
            session.delete(db_movie)
    session.commit()
    return json_movie


def get_or_create(model: Base, defaults: dict = None, is_commit: bool = False, **kwargs):
    """
    Find or create a new record for any Model in SQLAlchemy.

    :param model: SQLAlchemy model for creating.
    :param defaults: Dict with the default values.
    :param is_commit: Should we commit after creation.
    :param kwargs: All needed fields for the creation.
    :return: Instance of the creation object.
    """
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


def get_amount_of_movies_by_actor_and_year() -> List[dict]:
    """
    Search in the DB for amount of the movies grouped by actor and year.

    :return: The list with the dicts inside.
    """
    result = (
        session
        .query(cast.Actor.name.label("actor_name"),
               movie.Movie.year.label("year"),
               func.count(movie.Movie.id).label("amount_of_movies"))
        .join(cast.ActorMovie, cast.ActorMovie.actor_id == cast.Actor.id)
        .join(movie.Movie, movie.Movie.id == cast.ActorMovie.movie_id)
        .group_by(cast.Actor.name, movie.Movie.year)
        .all()
    )
    amount_schema = schemas.AmountMoviesByActorYear(many=True)
    return amount_schema.dump(result)


def create_bulk_movie_from_dict(json_movie: dict) -> None:
    """
    Create the movie, cast, genes (if they don't exists) from the dict.

    :param json_movie: Dict with the data about movie, cast and genres.
    """
    # TODO(*): Find out why PyCharm warn: Unexpected arguments in the SQLAlchemy models constructors
    db_movie = movie.Movie(
        title=json_movie['title'],
        year=json_movie['year'])
    session.add(db_movie)
    casts = []
    for actor_name in json_movie['cast']:
        try:
            schemas.actor_name_validator(actor_name)
            casts.append(get_or_create(cast.Actor, name=actor_name))
        except ValidationError as err:
            print(err.messages)
            print(err.valid_data)
    genres = list(map(lambda x: get_or_create(genre.Genre, name=x),
                               json_movie['genres']))
    for db_actor in casts:
        session.add(cast.ActorMovie(actor_id=db_actor.id, movie_id=db_movie.id))
    for db_genre in genres:
        session.add(genre.GenreMovie(genre_id=db_genre.id, movie_id=db_movie.id))
    session.commit()


def create_movie_from_dict(json_movie: dict) -> movie.Movie:
    """
    Create the movie, cast, genes from the dict.
    Cast and genres should be already in the DB

    :param json_movie: Dict with the data about movie, cast and genres (as IDs).
    :return: Created Movie instance.
    """
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
    return db_movie


def update_movie_from_dict(movie_id, json_movie: dict) -> movie.Movie:
    """
    Update the movie, cast, genes from the dict.
    Cast and genres should be already in the DB

    :param movie_id: ID of the DB movie.
    :param json_movie: Dict with the data about movie, cast and genres (as IDs).
    :return: Updated Movie instance.
    """
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
    return db_movie


def delete_cast_genres_from_movie(movie_id: int) -> None:
    """
    Helper function for get rid all related links from the Movie.

    :param movie_id: ID of the DB movie.
    """
    session.query(genre.GenreMovie).filter_by(movie_id=movie_id).delete()
    session.query(cast.ActorMovie).filter_by(movie_id=movie_id).delete()


def check_movie_exists(movie_id: int) -> bool:
    """
    Helper function checks if a movie exists.

    :param movie_id: ID of the DB movie.
    :return: The boolean result of the check.
    """
    return session.query(movie.Movie).get(movie_id) is not None


def kill_em_all() -> None:
    """Delete all the data from the database"""
    metadata = MetaData()
    metadata.reflect(bind=app.engine)

    for table in reversed(metadata.sorted_tables):
        session.execute(table.delete())
