# unittest assert methods: https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug
import unittest
import db
import os


class TestDatabase(unittest.TestCase):
    
    # starting this method with "test" is required by the unittest module
    def test_create_new_databases(self):
        # delte existing databases
        db.delete_databases()
        self.assertEquals(False, os.path.exists("record.db"))
        self.assertEquals(False, os.path.exists("foods.db"))
        # create new databases
        db.create_databases()
        self.assertEquals(True, os.path.exists("record.db"))
        self.assertEquals(True, os.path.exists("foods.db"))
        # TODO check content of new databases


if __name__ == "__main__":
    unittest.main()
