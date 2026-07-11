from math import radians, sin, cos, sqrt, atan2

# Conservative average speed assumption for a campus shuttle navigating
# gates, speed bumps and pedestrian traffic. Used only to produce a rough,
# clearly-labelled ETA estimate — not a routing-engine-accurate prediction.
AVERAGE_CAMPUS_SPEED_KMH = 20.0


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance in km between two lat/lng points."""
    if None in (lat1, lng1, lat2, lng2):
        return None
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lng2 - lng1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def eta_minutes(distance_km, avg_speed_kmh=AVERAGE_CAMPUS_SPEED_KMH):
    """Rough ETA in whole minutes for a given distance. Returns None if
    distance is unknown, and never returns less than 1 minute."""
    if distance_km is None:
        return None
    if distance_km <= 0:
        return 1
    minutes = (distance_km / avg_speed_kmh) * 60
    return max(1, round(minutes))
