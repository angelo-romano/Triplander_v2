import unittest
# from triplander.models.geo import Country


class TestMongo(unittest.TestCase):
    instance = None
    inserted_entries = None

    def setUp(self):
        #self.instance = MyTestModule()
        self.inserted_entries = set()

    def tearDown(self):
        self.instance.update
