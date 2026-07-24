from app.utils.geo import haversine_km


def distance_meters(lat1, lng1, lat2, lng2):
    km = haversine_km(lat1, lng1, lat2, lng2)
    return None if km is None else km * 1000


def within_radius(lat1, lng1, lat2, lng2, radius_meters):
    d = distance_meters(lat1, lng1, lat2, lng2)
    return d is not None and d <= radius_meters
