import numpy as np

import math

import random
from random import randint


# Generate random data for n days
# centervals are values average values for each month
# - Fixed error, that caused function to only generate 364 data points
#   we have rigged it to create 367 data points, one for each day in leap-year
#   and one data point for the following year
def generate_sample_data(intensity:float, seed:int=0, num_points:int=367, offset:float=0, ) -> [int]:
    """
    :param intensity: Number specifying size, amplitude
    :param seed: If given, same data with seed is generated
    :param num_points: Number of data points to generate
    :param offset: Offset to add to each data point
    """
    if seed != 0:
        random.seed(seed)
    centervals = [200,150,100, 75,75,75, 50, 75, 100, 150, 200, 250, 300]
    centervals = [x * intensity for x in centervals]
    inc = True
    value = centervals[0]
    value_arr = np.empty(num_points, dtype=int)
    for index in range(0,num_points):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int(index / 30)]
        dx = min(2.0, max(0.5, value / center ))
        value = value + randint(1,5) / dx if inc else value - randint( 1, 5) * dx
        #value = max(10, value)
        value_arr[index] = value + offset
    return value_arr
# END GenereateRandomYearDataList


# extract data from a list
# Todo: replace with slice when we have a better understanding of the code
def extract_data_interval(data, start, end):
    result = data[start : end]
    #print(f"extracted data from {start} to {end} length: {len(result)} source-length: {len(data)}")
    return result
# END extract_data_interval


# sample triple measurement data as a 2 dimensional grid
# - dim: dimensions of grid
# - res: resolution of grid
# - locations have coordinates and measurement values
# - preprocess_func: bake array into value [int] -> int
def generate_grid_samples(dim:tuple[int,int], res:tuple[int,int], locations):
    # calculate scale factor
    x_scale = dim[0] / res[0]
    y_scale = dim[1] / res[1]

    # allocate empty array
    result = np.empty((res[1], res[0]), dtype=int)

    # allocate point & sample the grid
    for iy in range(res[1]):
        for ix in range(res[0]):
            pt = [ix * x_scale, iy * y_scale]
            result[iy][ix] = get_estimated_value_at_point(locations, pt)

    return result
# END generate_grid_samples


#estimate NOX value based on the N measuring stations
# - locations: list of locations containing attributes [coordinates:tuple[int,int], measurement_value:int]
# - pt: point to estimate NOX value at
# Todo: we could combine distances and weights calculation since distances are only
#       used to calculate weight, but we keep it for now
# Todo: we could also use a more advanced weighting function, that mimics the original
# Todo: fix, our methods weighing and normalization is not correct
def get_estimated_value_at_point_ext(locations, pt):
    # define powerfactor so that small values mean more than big values in division
    power_factor = 2

    # distance to point from locations, add small value to avoid division by zero
    distances = [(math.dist(loc.coordinates, pt) + 1E-03) for loc in locations]

    # inverse distance weights with a power factor to emphasize closer points (chatgpt)
    weights = [1 / (dist ** power_factor) for dist in distances]

    # total weight is the sum of individual weights
    total_weight = np.sum(weights)

    # weighted value is the sum of each value multiplied by its corresponding weight (chatgpt)
    return np.sum([(weights[i] / total_weight) * locations[i].measurement_value for i in range(len(locations))])
# END get_estimated_value_at_point


# estimate NOX value based on the N measuring stations
def get_estimated_value_at_point_alt(locations, marked_point, power=4):
    # Initialize variables for total distance and the weighted NOX value
    total_weight = 0
    weighted_value = 0

    # Iterate over the stations (locations)
    for location in locations:
        # Calculate the distance between the marked point and the station
        dist = math.dist(location.coordinates, marked_point) + 1e-06

        # Avoid division by zero if the marked point is exactly at a station
        #if dist == 0:
            #return location.measurement_value  # If exactly at the station, return its NOX value

        # Calculate the weight based on the distance raised to the given power
        weight = (1 / dist) ** power
        total_weight += weight

        # Accumulate the weighted NOX values
        weighted_value += weight * location.measurement_value

    # Calculate the final NOX value as the weighted average
    return (weighted_value / total_weight) if total_weight != 0 else 0
# END get_estimated_value_at_point_ext


# estimate NOX value based on the N measuring stations
def get_estimated_value_at_point(locations, pt, power=1):
    dist_to_point = [math.dist(loc.coordinates, pt) for loc in locations]

    total_dist_to_point = sum(dist_to_point)

    num_locations = len(locations)
    dist_station_station = [math.dist(locations[i].coordinates, locations[(i + 1) % num_locations].coordinates) for i in range(num_locations)]

    total_station_to_station = sum(dist_station_station)

    val = sum([(1 - (dist_to_point[i] / total_dist_to_point)) * locations[i].measurement_value for i in range(num_locations)])
    val = val * (total_station_to_station / total_dist_to_point) ** power

    return val
# END get_estimated_value_at_point_ext
