"""
Distance calculation using Haversine formula.
"""
import math


class DistanceService:
    """Calculate distance between two points (lat/lng) in km."""

    R = 6371  # Earth radius in km

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Return distance in kilometers between (lat1, lon1) and (lat2, lon2)."""
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return DistanceService.R * c
