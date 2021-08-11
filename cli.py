"""
Functions and logic concerning the command line interface.
"""

import argparse


# define parsers
parser = argparse.ArgumentParser(
                description="A program to keep track of calories consumed each day.")
subparsers = parser.add_subparsers(
                help='command',
                dest='subparser_name')

add_food_parser = subparsers.add_parser(
                'add-food',
                help="Add food item to database.")

add_entry_parser = subparsers.add_parser(
                'add-entry',
                help="Add food entry to the record.")



# add-food arguments
add_food_parser.add_argument(
                'food-name',
                help="Name of food to be added to the database.",
                type=str)


# add-entry arguments
add_entry_parser.add_argument(
                'food-name',
                help="Name of food to be added to today's record.",
                type=str)

add_entry_parser.add_argument(
                '--portion-type',
                default='',
                help="Type of portion (e.g. cup, slice, bowl). Default=None.",
                metavar='',
                type=str)

add_entry_parser.add_argument(
                '--servings',
                default=1,
                help="Number of servings. Default=1.",
                metavar='',
                type=int)

add_entry_parser.add_argument(
                '--date',
                choices=['today', 'yesterday', 'DD/MM/YYYY'],
                default='today',
                help="Optionally specify a specific day the food should be added to. \
                        Default=today.",
                metavar='               {today,yesterday,DD/MM/YYYY}',
                type=str)



args = parser.parse_args()

if args.subparser_name == 'add-food':
    print('add-food subparser used')
    pass
elif args.subparser_name == 'add-entry':
    print('add-entry subparser used')
    pass
else:
    print('no subparser used')

print(args)
