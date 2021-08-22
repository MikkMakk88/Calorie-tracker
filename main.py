"""
Entry point of the script.
Contains most of the interface logic.
"""
from datetime import date, timedelta
import re

import db, cli

valid_date = r'^([\d]{1,2})([\d]{1,2})([\d]{4})?$'


def main():
    args = cli.parser.parse_args()

    if args.subparser_name == 'food':
        print('food subparser used')
        food_name = args.food
        portion_type = args.type
        calories = args.calories
        db.add_row_to_table(
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
            # match valid dates
            match = re.match(valid_date, args.date)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = match.group(3)
                if year:
                    year = int(year)
                else:
                    year = date.today().year
                entry_date = date(year, month, day)

        db.add_row_to_table(
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
