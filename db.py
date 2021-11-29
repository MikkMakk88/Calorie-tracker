"""
Classes to handle everything related to the database.
"""

import datetime
import re
import sqlite3
import logging
from os import path


class QueryData():

    valid_date_regex = r"^([\d]{1,2})-?([\d]{1,2})-?([\d]{4})?$"

    def __init__(
        self, date=None, food_name=None, portion_type=None, servings=None, calories=None
    ):
        self.date = self._parse_date(date)
        self.food_name = food_name
        self.portion_type = portion_type
        self.servings = servings
        self.calories = calories

        self.data = {
            "date": self.date,
            "food_name": self.food_name,
            "portion_type": self.portion_type,
            "servings": self.servings,
            "calories": self.calories,
        }

        logging.info("Created new QueryData instance: %s", self)

    def __repr__(self):
        output = []
        for key in self.data:
            output.append(f"{key}={self.data[key]}")

        return ", ".join(output)

    def parse_date_string_to_date_object(self, date_string):
        """
        Converts a string of the form "DD-MM-YYYY" or 'DDMMYYYY' (adding the year
        is optional) to a valid date object. Converting back can simply be done with
        the date.strftime() method.
        """
        match = re.match(QueryData.valid_date_regex, date_string)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = match.group(3)
            if year:
                year = int(year)
            else:
                year = datetime.date.today().year
            return datetime.date(year, month, day)

        raise Exception(f"Invalid date string {date_string}")

    def _parse_date(self, date):
        """
        This function is used to set the self.date variable according to whatever the
        date argument is. The argument can take on a few different forms, which this
        function will parse.
        """
        if date is None:
            return None

        if isinstance(date, datetime.date):
            return date

        entry_date = datetime.date.today()

        if date.lower() == "today":
            pass
        elif date.lower() == "tomorrow":
            entry_date += datetime.date.timedelta(days=1)
        elif date.lower() == "yesterday":
            entry_date -= datetime.date.timedelta(days=1)
        else:
            entry_date = self.parse_date_string_to_date_object(date)

        return entry_date

    def get_dict(self):
        """
        Return a dictionary containing only piecies of data that have a value.
        """
        return {key:value for key, value in self.data.items() if value is not None}

    def get_date_string(self):
        """
        Return self.date as a string formatted as: "dd-mm-YYYY".
        """
        return self.date.strftime("%d-%m-%Y")

    def get_query_set_string(self):
        """
        Returns contained data as a string which is correctly formatted to be directly
        passed to SQL to set data in a row.
        """
        logging.info("compiling query set string using data: %s", self)

        query_set_list = []
        data = self.get_dict()
        for key, val in data.items():
            if isinstance(val, str):
                query_set_list.append(f"{key} = '{val}'")
            elif isinstance(val, int):
                query_set_list.append(f"{key} = {val}")
            elif isinstance(val, datetime.date):
                val = val.strftime("%d-%m-%Y")
                query_set_list.append(f"{key} = '{val}'")

        return ", ".join(query_set_list)

    def get_query_match_string(self):
        """
        Returns contained data as a string which is correctly formatted to be directly
        passed to SQL as a search query.
        """
        logging.info("compiling match string using data: %s", self)

        output_data = dict(self.data)
        if output_data["date"]is not None:
            output_data["date"] = output_data["date"].strftime("%d-%m-%Y")

        match_string = " AND ".join(
            [
                f"{key} LIKE '%{value}%'" for key, value in output_data.items()
                if value is not None
            ]
        )

        return match_string


class CalorieCounterORM():
    """
    ORM to handle the database.
    """

    valid_date_regex = r"^([\d]{1,2})-?([\d]{1,2})-?([\d]{4})?$"

    def __init__(self, DB_PATH):
        self.DB_PATH = DB_PATH
        self.db_connection = None
        if not path.exists(self.DB_PATH):
            self.create_db_and_tables()

    def get_or_create_db_cursor(self):
        """
        Returns a cursor of the database connection. If one already exists then return
        it, if not then create a new one and return that.
        """
        if self.db_connection is None:
            logging.info("Creating new database connection")
            self.db_connection = sqlite3.connect(self.DB_PATH)

        logging.info("Supplying cursor to database connection")
        cursor = self.db_connection.cursor()

        return cursor

    def commit_changes(self):
        """
        Commits any changes and closes the database connection.
        """
        logging.info("Committing changes and closing database connection")
        self.db_connection.commit()
        self.db_connection.close()
        self.db_connection = None

    def create_db_and_tables(self):
        """
        Creates the database with the two separate tables.
        """
        cursor = self.get_or_create_db_cursor()

        logging.info("Creating new database and tables")
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

        self.commit_changes()

    def get_rows_from_table(self, table_name, match_data):
        """
        Retrieve all entries from specified table that fits the match_data. Always
        returns a list of none or more QueryData instances.

        Supplying no match_data is a valid search, in that case we return the entire
        table.
        """
        cursor = self.get_or_create_db_cursor()

        logging.info(
            "Getting rows from %s table that match %s", table_name, match_data
        )

        match_string = match_data.get_query_match_string()
        cursor.execute(
            f"""
            SELECT *
            FROM {table_name}
            WHERE {match_string}
            """
        )
        rows = cursor.fetchall()

        query_results = []
        if table_name == "foods":
            for row in rows:
                query_data = QueryData(
                    food_name=row[0],
                    portion_type=row[1],
                    calories=row[2]
                )
                query_results.append(query_data.get_dict())
        elif table_name == "record":
            for row in rows:
                query_data = QueryData(
                    date=row[0],
                    food_name=row[1],
                    portion_type=row[2],
                    servings=row[3]
                )
                query_results.append(query_data.get_dict())

        return query_results

    def add_row_to_table(self, table_name, new_data):
        """
        Adds new_data to the specified table.
        """
        cursor = self.get_or_create_db_cursor()

        if not new_data.food_name:
            logging.warn("No food_name given")
            return

        match_dict = new_data.get_dict()
        match_dict['servings'] = None
        match_data = QueryData(**match_dict)

        if table_name == "record":
            record_entries = self.get_rows_from_table(
                "record",
                match_data
            )

            if len(record_entries) > 1:
                raise Exception("More than one matching entry on record")
                return

            # increment servings count if entry already exists in the database
            if record_entries:
                logging.info(
                    "Food already exists at this date, incrementing servings count"
                )

                record_entry = record_entries[0]
                record_entry['servings'] += new_data.servings
                update_data = QueryData(**record_entry)

                self.update_row_in_table(
                    "record",
                    update_data,
                    match_data
                )
                return

            cursor.execute(
                """
                INSERT INTO record
                VALUES (
                    :date,
                    :food_name,
                    :portion_type,
                    :servings
                )
                """,
                {
                    "date": new_data.get_date_string(),
                    "food_name": new_data.food_name,
                    "portion_type": new_data.portion_type,
                    "servings": new_data.servings,
                },
            )

        elif table_name == "foods":
            match_data = QueryData(
                new_data.food_name,
                new_data.portion_type
            )
            food_exists = self.get_rows_from_table(
                "foods",
                match_data
            )
            if food_exists:
                logging.warn("Food already exists in database")
                return

            cursor.execute(
                """
                INSERT INTO foods
                VALUES (
                    :food_name,
                    :portion_type,
                    :calories
                )
                """,
                {
                    "food_name": new_data.food_name,
                    "portion_type": new_data.portion_type,
                    "calories": new_data.calories,
                },
            )

        self.commit_changes()

    def delete_rows_in_table(self, table_name, match_data):
        """
        Behaves similarly to get_rows_from_table() but deletes matching rows instead of
        returning them.
        """
        logging.info(
            "Deleting rows from %s table that match %s", table_name, match_data
        )

        cursor = self.get_or_create_db_cursor()

        match_string = query_data.get_query_match_string()

        self.commit_changes()

    def delete_table(self, table_name):
        """
        Delete given table.
        """
        logging.info("Deleting table %s", table_name)
        cursor = self.get_or_create_db_cursor()
        cursor.execute(
            f"""
            DROP
            TABLE IF EXISTS {table_name}
            """
        )
        self.commit_changes()

    def update_row_in_table(self, table_name, update_data, match_data):
        """
        Replace columns of all rows that match the match criteria.

        Columns that should be updated should be passed as kwargs in the form
        <column name>=<new data>, e.g:

        Targeting specific rows to be updated is done by passing kwargs in
        the form match_<column name>=<match criteria>.

        An example usage of this function might look like this:

            update_row_in_table('foods',
                match_food_name='broccoli', match_portion_type='head',
                calories=50
            )

        In this example case we update the calories value for a head of
        broccoli in the foods table.
        """
        logging.info(
            "Updating row in %s table with data: %s", table_name, update_data,
        )

        match_string = match_data.get_query_match_string()
        update_string = update_data.get_query_set_string()

        cursor = self.get_or_create_db_cursor()
        if table_name == "record":
            cursor.execute(
                f"""UPDATE record
                SET {update_string}
                WHERE {match_string}
                """
            )
        elif table_name == "foods":
            cursor.execute(
                f"""
                UPDATE foods
                SET {update_string}
                WHERE {match_string}
                """
            )

        self.commit_changes()
