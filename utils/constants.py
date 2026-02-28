"""
Shared constants for hirenow-core-api.
"""

# User roles (must match core.models.User.ROLE_CHOICES)
ROLE_CUSTOMER = "customer"
ROLE_WORKER = "worker"
ROLE_ADMIN = "admin"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Nearby workers (km)
DEFAULT_NEARBY_RADIUS_KM = 50
