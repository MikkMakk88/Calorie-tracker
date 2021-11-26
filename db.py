"""
ORM to handle the database.
"""
import datetime
import re
import sqlite3
import logging
from os import path


class ORM():
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
        Commits any changes and closes the database.
        """
        logging.info("Committing changes and closing database connection")
        self.db_connection.commit()
        self.db_connection.close()
        self.db_connection = None

    def convert_match_criteria_to_string(self, **match_criteria) -> str:
        """
        Takes criteria that should match a row in the database and constructs
        a string that is correctly formatted for an sqlite query.

        Match criteria should be passed as none or more kwargs in the
        form: match_<column name>=<search value>, e.g:

            match_food_name='broccoli', match_portion_type='head'
        """
        logging.info( "Converting match criteria to string: %s", str(match_criteria))
        if match_criteria.get("match_date"):
            match_criteria["match_date"] = datetime.date.strftime(
                match_criteria["match_date"], "%d-%m-%Y"
            )

        remove_prefix_regex = re.compile(r"^match_")
        match_string = " AND ".join(
            [
                f"{remove_prefix_regex.sub('', key)} LIKE '%{value}%'"
                for key, value in match_criteria.items()
                if bool(re.match("match_", key))
            ]
        )

        return match_string

    def parse_date_string_to_date_object(self, date_string):
        """
        Converts a string of the form "DD-MM-YYYY" or 'DDMMYYYY' (adding the year
        is optional) to a valid date object. Converting back can simply be done with
        the date.strftime() method.
        """
        match = re.match(ORM.valid_date_regex, date_string)
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

    def create_db_and_tables(self) -> None:
        """
        Creates the database with the two separate tables. This function probably only
        needs to be run once.
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

    def get_rows_from_table(self, table_name: str, **match_criteria) -> list:
        """
        Retrieve all entries from specified table that fits the
        match criteria.

        Match criteria should be passed as none or more kwargs in the
        form: match_<column name>=<match criteria>, e.g:

            match_food_name='broccoli', match_portion_type='head'

        Always returns a list of none or more dictionaries, with each
        dictionary containing the data of an individual row.
        """
        cursor = self.get_or_create_db_cursor()

        logging.info(
            "Getting rows from %s table that match %s", table_name, str(match_criteria)
        )
        match_string = self.convert_match_criteria_to_string(**match_criteria)
        # Supplying no match_criteria is a valid search,
        # in that case we return the entire table.
        if match_string:
            match_string = "WHERE " + match_string

        cursor.execute(
            f"""
            SELECT *
            FROM {table_name}
            {match_string}
        """
        )
        rows = cursor.fetchall()

        output_list = []
        if table_name == "foods":
            for row in rows:
                output_list.append(
                    {
                        "food_name": row[0],
                        "portion_type": row[1],
                        "calories": row[2],
                    }
                )
        elif table_name == "record":
            for row in rows:
                output_list.append(
                    {
                        "date": self.parse_date_string_to_date_object(row[0]),
                        "food_name": row[1],
                        "portion_type": row[2],
                        "servings": row[3],
                    }
                )

        return output_list

    def add_row_to_table(
        self,
        table_name: str,
        date: datetime.date = None,
        food_name: str = None,
        portion_type="",
        servings=1,
        calories=0,
    ) -> None:
        """
        Adds input data to table specified by table_name argument.

        Desired input data should be passed as an appropriate kwarg
        for each separate column, e.g:

            food_name='broccoli'

        Not specifying data for a column will cause it to revert to
        a default value, this is desired behavior.

        Note: food_name is required to perform a sensible query. It is
        only listed as a keyword argument for the sake of consistency
        with the other functions.

        This function will not check whether or not a matching entry
        is already present in the database.
        """
        cursor = self.get_or_create_db_cursor()

        if not food_name:
            logging.info("No food_name given")
            return

        # Check whether the food already exists in the foods database.
        food_exists = self.get_rows_from_table(
            "foods",
            match_food_name=food_name,
            match_portion_type=portion_type,
        )

        if table_name == "record":
            # # If the food doesn't exist in the foods db we prompt the user to add it
            # first if not food_exists:
            # # TODO impliment this logic
            # print('food not in db')
            # return

            # Create date object at function call time.
            if date is None:
                date = datetime.date.today()

            # Check if an entry with the given food exists on the given day.
            record_entries = self.get_rows_from_table(
                "record",
                match_date=date,
                match_food_name=food_name,
                match_portion_type=portion_type,
            )
            # If it does, we increment the 'servings' variable and return.
            if record_entries:
                logging.info(
                    "Food already exists at this date, incrementing servings count"
                )
                record_entry = record_entries[0]
                record_entry["servings"] += 1
                self.update_row_in_table(
                    "record",
                    **record_entry,
                    match_date=date,
                    match_food_name=food_name,
                    match_portion_type=portion_type,
                )
                return
            # Else we simply add the entry to the record table.
            cursor.execute(
                """
                INSERT INTO record
                VALUES (
                    :date,
                    :food_name,
                    :portion_type,
                    :servings
                )""",
                {
                    "date": datetime.date.strftime(date, "%d-%m-%Y"),
                    "food_name": food_name,
                    "portion_type": portion_type,
                    "servings": servings,
                },
            )

        elif table_name == "foods":
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
                )""",
                {
                    "food_name": food_name,
                    "portion_type": portion_type,
                    "calories": calories,
                },
            )

        self.commit_changes()

    def add_row_to_food_table(self, food_name, portion_type, calories) -> None:
        """
        Add a row to the food table.
        """
        logging.info(
            "Adding row to food table: %s, %s, %s",
            food_name,
            portion_type,
            str(calories),
        )
        self.add_row_to_table(
            "foods",
            food_name=food_name,
            portion_type=portion_type,
            calories=calories,
        )

    def add_row_to_record_table(self, food_name, portion_type, servings, date) -> None:
        """
        Add a row to the record table.
        """
        logging.info(
            "Adding row to record table: %s, %s, %s, %s",
            food_name,
            portion_type,
            str(servings),
            date,
        )

        entry_date = datetime.date.today()
        if date.lower() == "today":
            pass
        elif date.lower() == "tomorrow":
            entry_date += datetime.date.timedelta(days=1)
        elif date.lower() == "yesterday":
            entry_date -= datetime.date.timedelta(days=1)
        else:
            entry_date = self.parse_date_string_to_date_object(date)

        self.add_row_to_table(
            "record",
            food_name=food_name,
            portion_type=portion_type,
            servings=servings,
            date=entry_date,
        )

    def delete_rows_in_table(self, table_name: str, **match_criteria) -> None:
        """
        Behaves similarly to get_rows_from_table() but deletes matching
        rows instead of returning them.
        """
        logging.info(
            "Deleting rows from %s table that match %s", table_name, str(match_criteria)
        )
        if not match_criteria:
            logging.warn("No match_criteria passed.")
            return

        cursor = self.get_or_create_db_cursor()

        match_string = self.convert_match_criteria_to_string(**match_criteria)
        cursor.execute(
            f"""
            DELETE
            FROM {table_name}
            WHERE {match_string}
        """
        )

        self.commit_changes()

    def delete_table(self, table_name: str) -> None:
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

    def update_row_in_table(self, table_name: str, **update_and_match_criteria) -> None:
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
        logging.info("Updating row in %s table", table_name)
        match_string = self.convert_match_criteria_to_string(
            **update_and_match_criteria
        )

        query_set_list = []
        for key in update_and_match_criteria:
            val = update_and_match_criteria[key]
            if not re.match("match_", key):
                if isinstance(val, str):
                    query_set_list.append(f"{key} = '{val}'")
                elif isinstance(val, int):
                    query_set_list.append(f"{key} = {val}")
                elif isinstance(val, datetime.date):
                    val = val.strftime("%d-%m-%Y")
                    query_set_list.append(f"{key} = '{val}'")
        query_set_string = ", ".join(query_set_list)
        logging.info("Created SQL query string: \"%s\"", query_set_string)

        cursor = self.get_or_create_db_cursor()
        if table_name == "record":
            cursor.execute(
                f"""UPDATE record
                SET {query_set_string}
                WHERE {match_string}
                """
            )
        elif table_name == "foods":
            cursor.execute(
                f"""
                UPDATE foods
                SET {query_set_string}
                WHERE {match_string}
                """
            )

        self.commit_changes()
