import argparse
import logging
from src.helpers import get_db_uri
from src.crud import (
    scrape_ctis,
    update_location_coordinates,
)


def main():
    parser = argparse.ArgumentParser(description="ctis-scraper")
    parser.add_argument(
        "mode",
        choices=["scrape", "update_coordinates"],
        help="Mode of operation: 'scrape' or 'update_coordinates'",
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    DATABASE_URI = get_db_uri()

    if args.mode == "scrape":
        scrape_ctis(DATABASE_URI)

    elif args.mode == "update_coordinates":
        update_location_coordinates(DATABASE_URI)


if __name__ == "__main__":
    main()
