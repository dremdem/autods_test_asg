"""
Marshmallow schemas for the data validation

Import as:
import data_access_layer.schemas as schemas
"""


from marshmallow import Schema, fields


class GenreSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True)


class ActorSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True)


class MovieBaseSchema(Schema):
    title = fields.String()
    year = fields.Integer()


class MovieCreateBaseSchema(MovieBaseSchema):

    def __new__(cls):
        self = super().__new__(cls)
        self.title.required = True
        self.year.required = True


class CastGenresIDs(Schema):
    cast = fields.Pluck("ActorSchema", 'id', many=True)
    genres = fields.Pluck("GenreSchema", 'id', many=True)


class MovieBulkCreateSchema(MovieCreateBaseSchema):
    cast = fields.Pluck("ActorSchema", 'name', many=True)
    genres = fields.Pluck("GenreSchema", 'name', many=True)


class MovieCreateSchema(MovieCreateBaseSchema, CastGenresIDs):
    pass


class MovieUpdateSchema(MovieBaseSchema, CastGenresIDs):
    pass


class AmountMoviesByActorYear(Schema):
    actor_name = fields.String(required=True)
    year = fields.Integer(required=True)
    amount_of_movies = fields.Integer(required=True)
