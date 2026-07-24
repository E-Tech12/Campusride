import os
import requests

from app.utils.geo import haversine_km, eta_minutes as fallback_eta_minutes

ETA_PROVIDER = os.getenv("ETA_PROVIDER", "").lower()  # "google", "mapbox", or "" for fallback-only
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")


def _google_eta(origin_lat, origin_lng, dest_lat, dest_lng):
    resp = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        params={
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{dest_lat},{dest_lng}",
            "mode": "driving",
            "key": GOOGLE_MAPS_API_KEY,
        },
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    element = data["rows"][0]["elements"][0]
    if element.get("status") != "OK":
        return None
    return {
        "distance_km": round(element["distance"]["value"] / 1000.0, 2),
        "eta_minutes": max(1, round(element["duration"]["value"] / 60.0)),
        "source": "google_maps",
    }


def _mapbox_eta(origin_lat, origin_lng, dest_lat, dest_lng):
    resp = requests.get(
        f"https://api.mapbox.com/directions/v5/mapbox/driving/"
        f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}",
        params={"access_token": MAPBOX_ACCESS_TOKEN, "overview": "false"},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    routes = data.get("routes") or []
    if not routes:
        return None
    route = routes[0]
    return {
        "distance_km": round(route["distance"] / 1000.0, 2),
        "eta_minutes": max(1, round(route["duration"] / 60.0)),
        "source": "mapbox",
    }


def get_eta(origin_lat, origin_lng, dest_lat, dest_lng):
    """Real routing-based distance/ETA when a provider is configured;
    otherwise falls back to the existing haversine + average-speed estimate
    so the feature degrades gracefully in dev environments without API keys."""
    if None in (origin_lat, origin_lng, dest_lat, dest_lng):
        return {"distance_km": None, "eta_minutes": None, "source": "unavailable"}

    try:
        if ETA_PROVIDER == "google" and GOOGLE_MAPS_API_KEY:
            result = _google_eta(origin_lat, origin_lng, dest_lat, dest_lng)
            if result:
                return result
        elif ETA_PROVIDER == "mapbox" and MAPBOX_ACCESS_TOKEN:
            result = _mapbox_eta(origin_lat, origin_lng, dest_lat, dest_lng)
            if result:
                return result
    except requests.RequestException:
        pass  # fall through to estimate below

    distance_km = haversine_km(origin_lat, origin_lng, dest_lat, dest_lng)
    return {
        "distance_km": round(distance_km, 2) if distance_km is not None else None,
        "eta_minutes": fallback_eta_minutes(distance_km),
        "source": "estimate",
    }
