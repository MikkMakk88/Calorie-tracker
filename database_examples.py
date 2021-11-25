"""
Examples of how database rows should be structured.
"""

from datetime import date

record_entry1 = {
    "date": date(2020, 7, 14),
    "food_name": "broccoli",
    "portion_type": "head",
    "servings": 1,
}

food_entry1 = {
    "food_name": "broccoli",
    "portion_type": "head",
    "calories": 30,
}

food_entry2 = {
    "food_name": "toast with butter",
    "portion_type": "slice",
    "calories": 120,
}
