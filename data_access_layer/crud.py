"""
Pure DB operations

Import as:
import sql_app.crud as crud
"""

import datetime as dt
from sqlalchemy.orm import Session

import data_access_layer.model.cast as cast
import data_access_layer.model.genre as genre
import data_access_layer.model.movie as movie
