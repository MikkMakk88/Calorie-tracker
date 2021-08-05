"""
Examples of how database rows should be structured.
"""

record_entry1 = {
    "date":"06-06-1990",
    "food_name":"broccoli",
    "portion_type":"head",
    "servings":1
}

food_entry1 = {
    "food_name":"broccoli",
    "portion_type":"head",
    "includes_foods":[
    ],
    "base_calories":30
}

food_entry2 = {
    "food_name":"toast with butter",
    "portion_type":"slice",
    "includes_foods":[
        ["bread","slice",1],
        ["butter","spread",1]
    ],
    "base_calories":0
}
        