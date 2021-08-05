# Currently I'm not quite sure how to implement unit testing (or just testing in general) on a database
# I'm going to merge this back into the master branch for now and come back to it later.

# unittest assert methods: https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug
import unittest
import db
import os

db_path = "test_db.db"


# used to first test creation and deletion of database
class TestDatabaseWithoutSetUp(unittest.TestCase):

    def test_create_db(self):
        self.assertEqual(False, os.path.exists(db_path))
        db.create_db_and_tables(db_path)
        self.assertEqual(True, os.path.exists(db_path))
        os.remove(db_path)
        self.assertEqual(False, os.path.exists(db_path))


class TestDatabaseWithSetUp(unittest.TestCase):

    # TODO set this up with mock databases
    def setUp(self):
        db.create_db_and_tables(db_path)   

    def tearDown(self):
        os.remove(db_path)

    # starting thest methods with "test" is required by the unittest module
    def test_get_empty_rows(self):
        record_rows = db.get_rows_from_table(db_path, "record")
        foods_rows = db.get_rows_from_table(db_path, "foods")
        self.assertEqual([], record_rows)
        self.assertEqual([], foods_rows)

    def test_add_rows(self):
        pass

    def test_remove_rows(self):
        pass

    def test_delete_table(self):
        pass
    
    def test_create_tables_after_deletion(self):
        pass

    def test_update_rows(self):
        pass
        

if __name__ == "__main__":
    unittest.main()
