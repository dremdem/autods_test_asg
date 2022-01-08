"""
Marshmallow schemas for the data validation

Import as:
import data_access_layer.schemas as schemas
"""

from marshmallow import Schema, fields, ValidationError

ACTOR_NAME_STOP_CHARS = '$()?'


class GenreSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True)


def actor_name_validator(actor_name: str):
    if any([char in ACTOR_NAME_STOP_CHARS for char in actor_name]):
        raise ValidationError(f"The actor name: {actor_name} is not valid.")


class ActorSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True, validate=actor_name_validator)


class MovieBaseSchema(Schema):
    title = fields.String()
    year = fields.Integer()


class MovieCreateBaseSchema(MovieBaseSchema):

    def __new__(cls):
        # TODO(*): Too hacky, need to refactor this
        self = super().__new__(cls)
        self._declared_fields['title'].required = True
        self._declared_fields['year'].required = True
        return self


class CastGenresIDs(Schema):
    cast = fields.Pluck("ActorSchema", 'id', many=True)
    genres = fields.Pluck("GenreSchema", 'id', many=True)


class MovieBulkCreateSchema(MovieCreateBaseSchema):
    cast = fields.Pluck("ActorSchema", 'name', many=True)
    genres = fields.Pluck("GenreSchema", 'name', many=True)


class MovieReturnSchema(MovieCreateBaseSchema):
    id = fields.Integer(required=True)


class MovieCreateSchema(MovieCreateBaseSchema, CastGenresIDs):
    pass


class MovieUpdateSchema(MovieBaseSchema, CastGenresIDs):
    pass


class AmountMoviesByActorYear(Schema):
    actor_name = fields.String(required=True)
    year = fields.Integer(required=True)
    amount_of_movies = fields.Integer(required=True)
