from unittest import TestCase

import data_access_layer.services as services


class Test(TestCase):

    def setUp(self):
        pass

    def test_update_movie_from_dict(self):
        services.delete_cast_genres_from_movie()
        self.fail()
