"""
Marshmallow schemas for the data validation

Import as:
import data_access_layer.schemas as schemas
"""


from marshmallow import Schema, fields


class GenreSchema(Schema):
    name = fields.String(required=True)


class ActorSchema(Schema):
    name = fields.String(required=True)


class MovieCreateSchema(Schema):
    title = fields.String(required=True)
    year = fields.Integer(required=True)

    cast = fields.Pluck("ActorSchema", 'name', many=True)
    genres = fields.Pluck("GenreSchema", 'name', many=True)

