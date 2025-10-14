"""CLI for geocoding utilities."""

import argparse

from ..geocode.geopy import geocode, reverse_geocode, get_location_info
from ..core.logging import get_logger, set_log_level

def main():
    """Main CLI entry point for geocoding."""
    parser = argparse.ArgumentParser(description='Geocoding utilities')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Forward geocoding
    forward_parser = subparsers.add_parser('forward', help='Convert address to coordinates')
    forward_parser.add_argument('address', help='Address to geocode')
    
    # Reverse geocoding
    reverse_parser = subparsers.add_parser('reverse', help='Convert coordinates to address')
    reverse_parser.add_argument('latitude', type=float, help='Latitude')
    reverse_parser.add_argument('longitude', type=float, help='Longitude')
    
    # Location info
    info_parser = subparsers.add_parser('info', help='Get detailed location info')
    info_parser.add_argument('address', help='Address to get info for')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        set_log_level('DEBUG')
    
    log = get_logger(__name__)
    
    if args.command == 'forward':
        result = geocode(args.address)
        if result:
            lat, lon = result
            print(f"Coordinates: {lat}, {lon}")
        else:
            print("Could not geocode address")
            exit(1)
    
    elif args.command == 'reverse':
        result = reverse_geocode(args.latitude, args.longitude)
        if result:
            print(f"Address: {result}")
        else:
            print("Could not reverse geocode coordinates")
            exit(1)
    
    elif args.command == 'info':
        result = get_location_info(args.address)
        if result:
            print(f"Address: {result['address']}")
            print(f"Coordinates: {result['latitude']}, {result['longitude']}")
        else:
            print("Could not get location info")
            exit(1)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()