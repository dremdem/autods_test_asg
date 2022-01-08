# AutoDS test assignment

## Projects structure

```
root
|   autods_local.yaml: OpenAPI project specification
|   autods_test_asgn.drawio: ER-diagramm of the project.
|___api
|     app.py: The main flask app. 
|__data
|      amount_of_movies_by_actor_and_year.sql: SQL-query for the report endpoint.
|      movie_create.http
|      movie_delete.http
|      movie_update.http
|      movies.json
|      report.http
|__data_access_layer
   |   db: SQLLite db-file
   |   movie_bulk_upload.py: Script for initial data loading.
   |   schemas.puml: One of possible UML class diagramm (outdated).
   |   schemas.py: Marshmellow schemas for the data validation.
   |   services.py: All-in-one services that support the logic and DB operations.           
   |___migrations: alembic migrations
   |___model: SQLAlchemy DB models
```

## Requirements

- Python 3.8
- Pipenv

## Installing

### Clone the repo

```shell
git clone https://github.com/dremdem/autods_test_asg.git test_autods
cd test_autods
pipenv install
pipenv shell
export PYTHONPATH=$(pwd)
```

### Populate the data

```shell
python data_access_layer/movie_bulk_upload.py data/movies.json -d
```

### Run the test server

```shell
python api/app.py
```

## Usage and testing

### Create a movie

```shell
curl -X POST --location "http://localhost:8000/movie" \
    -H "Content-Type: application/json" \
    -d '{
          "title": "Bananas in the Space!",
          "year": 2022,
          "cast": [
            25,
            31,
            32
          ],
          "genres": [
            14,
            3,
            36
          ]
        }'
```

### Update the movie

```shell
curl -X PUT --location "http://localhost:8000/movie/10" \
    -H "Content-Type: application/json" \
    -d '{
          "title": "New Life Rescue - 4",
          "year": 2026,
          "cast": [
            25
          ],
          "genres": [
            14
          ]
        }'
```

### Delete the movie

```shell
curl -X DELETE --location "http://localhost:8000/movie/11"
```

### Get the report

```shell
curl -X GET --location "http://localhost:8000/report"
```

## OpenAPI

https://app.swaggerhub.com/apis/dremdem/autods/1.0.0


## Links

https://marshmallow.readthedocs.io/en/stable/
https://marshmallow.readthedocs.io/en/stable/nesting.html
https://flask-marshmallow.readthedocs.io/en/latest/
https://habr.com/ru/post/246699/
https://www.jetbrains.com/help/idea/openapi.html#remote-spec
https://plugins.jetbrains.com/plugin/16890-endpoints
https://stackoverflow.com/questions/14343740/flask-sqlalchemy-or-sqlalchemy
https://web.archive.org/web/20190901011222/http://derrickgilland.com/posts/demystifying-flask-sqlalchemy/
https://flask-sqlalchemy.palletsprojects.com/en/2.x/
https://stackoverflow.com/questions/39891387/better-way-convert-json-to-sqlalchemy-object/39891537
https://marshmallow.readthedocs.io/en/stable/examples.html
https://flask-restful.readthedocs.io/en/latest/
https://www.jetbrains.com/help/pycharm/http-client-in-product-code-editor.html
https://swagger.io/specification/
