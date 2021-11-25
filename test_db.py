"""
Unit tests for db.py
"""

# pylint: disable=missing-function-docstring

import sqlite3
import unittest
from unittest.case import TestCase
from datetime import date

import db


class TestCreateDatabase(TestCase):
    """
    Test the creation of a new database
    """

    def test_create_db(self):
        with sqlite3.connect(":memory:") as db_connection:
            # first verify that database has no tables
            cursor = db_connection.cursor()
            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
            """
            )
            query = cursor.fetchall()
            self.assertFalse(("record",) in query)
            self.assertFalse(("foods",) in query)
            db.create_db_and_tables(db_connection)
            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
            """
            )
            query = cursor.fetchall()
            self.assertTrue(("record",) in query)
            self.assertTrue(("foods",) in query)


class TestDatabaseWithEmptyTables(TestCase):
    """
    Run tests on databases that have tables but no data
    """

    def setUp(self):
        self.db_connection = sqlite3.connect(":memory:")
        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS record (
                date text,
                food_name text,
                portion_type text,
                servings integer
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS foods (
                food_name text,
                portion_type text,
                calories integer
            )
        """
        )
        self.db_connection.commit()

    def tearDown(self):
        self.db_connection.close()

    def test_get_empty_rows(self):
        record_rows = db.get_rows_from_table(self.db_connection, "record")
        foods_rows = db.get_rows_from_table(self.db_connection, "foods")
        self.assertEqual([], record_rows)
        self.assertEqual([], foods_rows)

    def test_add_row_to_record_table(self):
        db.add_row_to_table(
            self.db_connection, "record", food_name="broccoli", date=date(2020, 5, 15)
        )

        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM record
        """
        )
        rows = cursor.fetchall()
        self.assertEqual(rows, [("15-05-2020", "broccoli", "", 1)])

    def test_add_row_to_foods_table(self):
        db.add_row_to_table(
            self.db_connection, "foods", food_name="broccoli", calories=50
        )

        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM foods
        """
        )
        rows = cursor.fetchall()
        self.assertEqual(rows, [("broccoli", "", 50)])

    # def test_add_row_prompts_user(self):
    #     pass


class TestDatabaseWithData(TestCase):
    """
    Run tests on databases that have test data
    """

    def setUp(self):
        self.db_connection = sqlite3.connect(":memory:")
        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS record (
                date text,
                food_name text,
                portion_type text,
                servings integer
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS foods (
                food_name text,
                portion_type text,
                calories integer
            )
        """
        )
        cursor.execute(
            """
            INSERT INTO record
            VALUES (
                '15-05-2020',
                'broccoli',
                'head',
                1
        )"""
        )
        cursor.execute(
            """
            INSERT INTO record
            VALUES (
                '19-10-1895',
                'apple sauce',
                'jar',
                5
        )"""
        )
        cursor.execute(
            """
            INSERT INTO foods
            VALUES (
                'coffee',
                'with milk',
                100
        )"""
        )
        cursor.execute(
            """
            INSERT INTO foods
            VALUES (
                'coffee',
                'black',
                30
        )"""
        )
        cursor.execute(
            """
            INSERT INTO foods
            VALUES (
                'apple sauce',
                'jar',
                200
        )"""
        )
        self.db_connection.commit()

    def tearDown(self):
        self.db_connection.close()

    def test_get_rows_with_no_match_critera(self):
        record_rows = db.get_rows_from_table(self.db_connection, "record")
        foods_rows = db.get_rows_from_table(self.db_connection, "foods")
        self.assertEqual(len(record_rows), 2)
        self.assertEqual(len(foods_rows), 3)

    def test_get_rows_with_single_match_criteria(self):
        record_rows = db.get_rows_from_table(
            self.db_connection, "record", match_food_name="apple sauce"
        )
        self.assertEqual(
            record_rows[0],
            {
                "date": date(1895, 10, 19),
                "food_name": "apple sauce",
                "portion_type": "jar",
                "servings": 5,
            },
        )
        foods_rows = db.get_rows_from_table(
            self.db_connection, "foods", match_food_name="apple sauce"
        )
        self.assertEqual(
            foods_rows[0],
            {"food_name": "apple sauce", "portion_type": "jar", "calories": 200},
        )

    def test_get_rows_with_multiple_match_criteria(self):
        record_rows = db.get_rows_from_table(
            self.db_connection,
            "record",
            match_food_name="apple sauce",
            match_portion_type="jar",
            match_date=date(1895, 10, 19),
        )
        self.assertEqual(
            record_rows[0],
            {
                "date": date(1895, 10, 19),
                "food_name": "apple sauce",
                "portion_type": "jar",
                "servings": 5,
            },
        )
        foods_rows = db.get_rows_from_table(
            self.db_connection,
            "foods",
            match_food_name="apple sauce",
            match_portion_type="jar",
            match_calories=200,
        )
        self.assertEqual(
            foods_rows[0],
            {"food_name": "apple sauce", "portion_type": "jar", "calories": 200},
        )

    def test_delete_rows(self):
        db.delete_rows_in_table(
            self.db_connection, "foods", match_food_name="apple sauce"
        )
        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM foods
        """
        )
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2)

    def test_update_row_in_foods_table(self):
        db.update_row_in_table(
            self.db_connection,
            "foods",
            match_food_name="coffee",
            match_portion_type="black",
            calories=50,
            portion_type="black with sugar",
        )

        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM foods
            WHERE
                food_name = 'coffee' AND
                portion_type = 'black'
        """
        )
        rows = cursor.fetchall()
        self.assertEqual(rows, [])

        cursor.execute(
            """
            SELECT *
            FROM foods
            WHERE
                food_name = 'coffee' AND
                portion_type = 'black with sugar'
        """
        )
        rows = cursor.fetchall()
        self.assertEqual(rows[0], ("coffee", "black with sugar", 50))

    # def test_update_row_in_record_table(self):
    #     pass

    def test_increase_servings_count_in_record_table(self):
        db.add_row_to_table(
            self.db_connection,
            "record",
            date=date(2020, 5, 15),
            food_name="broccoli",
            portion_type="head",
        )

        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM record
            WHERE food_name = 'broccoli'
        """
        )
        rows = cursor.fetchall()
        self.assertEqual(rows[0], ("15-05-2020", "broccoli", "head", 2))


if __name__ == "__main__":
    unittest.main()
