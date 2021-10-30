"""
Entry point of the script.
Contains most of the interface logic.
"""

from datetime import date, timedelta
import sqlite3

import db
import cli
import cfg
from utilities import parse_date_string_to_date_object


def main():
    args = cli.parser.parse_args()
    with sqlite3.connect(cfg.DB_PATH) as db_connection:

        if args.subparser_name == 'food':
            print('food subparser used')
            food_name = args.food
            portion_type = args.type
            calories = args.calories
            db.add_row_to_table(
                db_connection,
                'foods',
                food_name=food_name,
                portion_type=portion_type,
                calories=calories
            )

        elif args.subparser_name == 'entry':
            print('entry subparser used')
            food_name = args.food
            portion_type = args.type
            servings = args.servings

            entry_date = date.today()
            if args.date.lower() == 'tomorrow':
                entry_date += timedelta(days=1)
            elif args.date.lower() == 'yesterday':
                entry_date -= timedelta(days=1)
            else:
                entry_date = parse_date_string_to_date_object(args.date)

            db.add_row_to_table(
                db_connection,
                'record',
                food_name=food_name,
                portion_type=portion_type,
                servings=servings,
                date=entry_date
            )

        else:
            print('no subparser used')


if __name__ == '__main__':
    main()
