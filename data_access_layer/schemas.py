"""
Marshmallow schemas for the data validation

Import as:
import data_access_layer.schemas as schemas
"""


from marshmallow import Schema, fields


class GenreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)


class ActorSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)


class MovieBaseSchema(Schema):
    title = fields.String(required=True)
    year = fields.Integer(required=True)


class MovieBulkCreateSchema(MovieBaseSchema):
    cast = fields.Pluck("ActorSchema", 'name', many=True)
    genres = fields.Pluck("GenreSchema", 'name', many=True)


class MovieCreateSchema(MovieBaseSchema):
    cast = fields.Pluck("ActorSchema", 'id', many=True)
    genres = fields.Pluck("GenreSchema", 'id', many=True)

