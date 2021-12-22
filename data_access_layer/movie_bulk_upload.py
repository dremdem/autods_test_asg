"""
Bulk upload movies from JSON-file

Import as:
import data_access_layer.movie_bulk_upload as movie_bulk_upload
"""
import datetime as dt
import argparse
import json
import logging

import tqdm

import data_access_layer.services as services
import data_access_layer.schemas as schemas


logger = logging.getLogger(__name__)


def upload(filename: argparse.FileType) -> None:
    """
    Upload movies from the JSON-file

    The schema of the file:
        [
          {
            "title": "After Dark in Central Park",
            "year": 1900,
            "cast": [],
            "genres": []
          },
          {
            "title": "The Reluctant Astronaut",
            "year": 1967,
            "cast": [
              "Don Knotts",
              "Leslie Nielsen"
            ],
            "genres": [
              "Comedy"
            ]
          },
        ]

    :param filename: Path to the JSON file.
    """
    logger.info("Start movies bulk upload.")
    data = json.load(filename)
    for json_movie in tqdm.tqdm(data):
        if services.validate_movie(schemas.MovieBulkCreateSchema, json_movie):
            services.create_movie_from_dict(json_movie)
    logger.info("Movies uploaded successfully.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Movie bulk loader')
    parser.add_argument(
        "filepath",
        help='File path to JSON-file with the movies that have to be imported.',
        type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument(
        "-l",
        "--log-level",
        default=logging.INFO,
        type=lambda x: getattr(logging, x),
        help="Configure the logging level.")
    parser.add_argument(
        "-d",
        "--delete",
        action='store_true',
        help='Delete the data before the upload.')
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    logger.info(f"Movie bulk loader started at:"
                f"{dt.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} "
                f"for the file: {args.filepath.name}")
    if args.delete:
        services.kill_em_all()
    upload(args.filepath)



