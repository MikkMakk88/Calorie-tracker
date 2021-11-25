"""
Functions and logic concerning the command line interface.
"""

import argparse


# define parsers
parser = argparse.ArgumentParser(
    description="A program to keep track of calories consumed each day."
)
subparsers = parser.add_subparsers(help="command", dest="subparser_name")

food_parser = subparsers.add_parser("food", help="Add food item to database.")

entry_parser = subparsers.add_parser("entry", help="Add food entry to the record.")


# def arguments of food subparser
food_parser.add_argument(
    "food", help="Name of food to be added to the database.", type=str
)

food_parser.add_argument(
    "calories", help="How many calories the food contains.", type=str
)

food_parser.add_argument(
    "--type",
    metavar="",
    help="Type of portion (e.g. cup, slice, bowl), default=None.",
    type=str,
)


# define arguments of entry subparser
entry_parser.add_argument(
    "food", help="Name of food to be added to today's record.", type=str
)

entry_parser.add_argument(
    "--type",
    default="",
    help="Type of portion (e.g. cup, slice, bowl), default=None.",
    metavar="",
    type=str,
)

entry_parser.add_argument(
    "--servings", default=1, help="Number of servings, default=1.", metavar="", type=int
)

entry_parser.add_argument(
    "--date",
    default="today",
    help="Optionally specify a date, default=today.",
    metavar="               {today,yesterday,tomorrow,DDMM(YYYY)}",
    type=str,
)


# debug
if __name__ == "__main__":
    args = parser.parse_args()

    try:
        if args.subparser_name == "food":
            print("food subparser used")
            food_name = args.food
            calories = args.calories
            portion_type = args.type
            print(food_name, calories, portion_type)

        elif args.subparser_name == "entry":
            print("entry subparser used")

        else:
            print("no subparser used")
    except AttributeError as e:
        print("ERROR:", e)

    print(args)
    print("subparser name: ", args.subparser_name)
