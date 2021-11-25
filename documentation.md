# Calorie Tracker Documentation

---
---
# db.py


#### The database includes 2 tables:


<br>

### foods 
Each row in the table represents a separate food item.

Columns stored in the table are:
- food_name
	- Self explanatory
- portion_type
	- Each food has 1 or more associated portion types (glass, spoon, slice, etc).
	- Each portion type of a particular food is treated as a separate row in the table.
      but will be grouped together under the common food name when presented to the user.
	- Omitting a portion type is allowed on the user end, this will simply be treated as.
      it's own row where the portion type is an empty string.
- includes_foods
	- This acts sort of like an ingredients list which allows foods to be supersets
      of other foods. each row in this list must be a list containing food name, 
      portion type and number of servings of a food already present in the table.
- base_calories
	- When a food cannot be constructed purely as a superset of other foods
      an integer of calories can be added. This is also useful for defining atomized foods.

#### Examples

```
food_entry1 = {
    "food_name":"broccoli",
    "portion_type":"head",
    "includes_foods":[
    ],
    "base_calories":30
}
```

```
food_entry2 = {
    "food_name":"toast with butter",
    "portion_type":"slice",
    "includes_foods":[
        ["bread","slice",1],
        ["butter","spread",1]
    ],
    "base_calories":0
}
```

<br>

### record
Each row in the table represents one consumed food item. 

Columns stored in the table are:
- date: 
	- String in the form "dd-mm-yyyy"
- food_name: 
	- String, corresponding to the same name as in the foods table
- portion_type:
	- String, corresponding to the same name as in the foods table
- servings:
	- Integer, number of items consumed

#### Example

```
record_entry1 = {
    "date":"06-06-1990",
    "food_name":"broccoli",
    "portion_type":"head",
    "servings":1
}
```
