"""Geocoding utilities using geopy (when available)."""

from typing import Optional, Tuple, Dict, Any

from ..core.logging import get_logger

log = get_logger(__name__)

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    log.warning("geopy not available. Install with: pip install geopy")

def check_geopy() -> bool:
    """Check if geopy is available."""
    return GEOPY_AVAILABLE

def geocode(address: str, timeout: int = 10) -> Optional[Tuple[float, float]]:
    """Convert address to coordinates (latitude, longitude)."""
    if not GEOPY_AVAILABLE:
        log.error("geopy not available")
        return None
    
    try:
        geolocator = Nominatim(user_agent="pyutils/1.0.0")
        location = geolocator.geocode(address, timeout=timeout)
        
        if location:
            return (location.latitude, location.longitude)
        else:
            log.warning(f"Could not geocode address: {address}")
            return None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        log.error(f"Geocoding error: {e}")
        return None
    except Exception as e:
        log.error(f"Unexpected geocoding error: {e}")
        return None

def reverse_geocode(latitude: float, longitude: float, 
                   timeout: int = 10) -> Optional[str]:
    """Convert coordinates to address."""
    if not GEOPY_AVAILABLE:
        log.error("geopy not available")
        return None
    
    try:
        geolocator = Nominatim(user_agent="pyutils/1.0.0")
        location = geolocator.reverse((latitude, longitude), timeout=timeout)
        
        if location:
            return location.address
        else:
            log.warning(f"Could not reverse geocode: {latitude}, {longitude}")
            return None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        log.error(f"Reverse geocoding error: {e}")
        return None
    except Exception as e:
        log.error(f"Unexpected reverse geocoding error: {e}")
        return None

def get_location_info(address: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """Get detailed location information."""
    if not GEOPY_AVAILABLE:
        log.error("geopy not available")
        return None
    
    try:
        geolocator = Nominatim(user_agent="pyutils/1.0.0")
        location = geolocator.geocode(address, timeout=timeout)
        
        if location:
            return {
                'address': location.address,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'raw': location.raw
            }
        else:
            return None
            
    except Exception as e:
        log.error(f"Error getting location info: {e}")
        return None

# Fallback implementations without geopy
def simple_geocode_fallback(address: str) -> Optional[Tuple[float, float]]:
    """Fallback geocoding without geopy (very limited)."""
    log.warning("Using fallback geocoding - install geopy for better results")
    
    # This is a very basic fallback - in practice you'd use a web API
    known_locations = {
        'new york': (40.7128, -74.0060),
        'london': (51.5074, -0.1278),
        'paris': (48.8566, 2.3522),
        'tokyo': (35.6762, 139.6503),
        'sydney': (-33.8688, 151.2093)
    }
    
    address_lower = address.lower()
    for city, coords in known_locations.items():
        if city in address_lower:
            return coords
    
    return None