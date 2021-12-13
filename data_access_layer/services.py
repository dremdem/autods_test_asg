"""
All logic and DB operations placed here.

Import as:
import data_access_layer.services as services
"""

import datetime as dt

from marshmallow import ValidationError
from sqlalchemy.orm import Session

import data_access_layer.model.cast as cast
import data_access_layer.model.genre as genre
import data_access_layer.model.movie as movie
import data_access_layer.schemas as schemas


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

