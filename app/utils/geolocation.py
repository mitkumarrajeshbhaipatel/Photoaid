from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # Radius of Earth in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) ** 2
    c = 2 * asin(sqrt(a))

    distance = R * c
    return distance
