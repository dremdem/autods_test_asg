from sqlalchemy import Column, ForeignKey, Integer, String

from .base import Base

metadata = Base.metadata


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(1))


class GenreMovie(Base):
    __tablename__ = 'genre_movie'

    id = Column(Integer, primary_key=True)
    genre_id = Column(ForeignKey('genre.id'))
    movie_id = Column(ForeignKey('movie.id'))
