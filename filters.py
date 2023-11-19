FUEL_COST_PER_MILE = 1.38
AVERAGE_SPEED = 65

""" What is the absolute minimum estimated hourly wage of a job """
MINIMUM_DESIRED_HOURLY_WAGE = 15

""" 
How much should we multiply the straight line mileage from one location to another to
give a more realistic mileage estimate
"""
CORRECTION_FACTOR = 1.2

TIME_THRESHOLD = 60
""" max desired number of notifications within the above time frame """
MAX_DESIRED_NOTIFICATIONS = 3

""" 
For truckers with short preference.
How bad is it to end a delivery far from the first pinged location (hypothesized to be home)? (range: 0-1)
    0 -> Doesn't matter
    1 -> Quintessential 
"""
FAR_FROM_HOME_PENALTY_RATIO_SHORT = 0.2

""" 
For truckers with long preference.
How bad is it to end a delivery far from the first pinged location (hypothesized to be home)? (range: 0-1)
    0 -> Doesn't matter
    1 -> Quintessential 
"""
FAR_FROM_HOME_PENALTY_RATIO_LONG = 0

# What should be the radius in miles of what we consider to be "near"
NEARBY_RANGE = 30

# How important is it to end a delivery in an area with high load density (range: 0-1)
# 0 -> Doesn't matter
# 1 -> Quintessential
DENSITY_RATIO = 0.3

# How important is it to end a delivery in an area with high-paying loads (range: 0-1)
# 0 -> Doesn't matter
# 1 -> Quintessential
HIGH_PAYING_LOADS_RATIO = 0.3

# True/False. Bin the loads together in a grid of the USA for optimal calculation
# False to get more accurate results which are significantly more expensive
USE_GRID = True

# Size in degree of the sides of the cells that make up the grid of the map
# Smaller sizes leads to slower but more accurate results
GRID_DEGREE_INCREMENT = 10
