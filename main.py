import os
import argparse

from dotenv import load_dotenv

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
    load_dotenv()  # load dotenv when running locally
    DATABASE_URI = os.getenv("DATABASE_URI")

    if args.mode == "scrape":
        scrape_ctis(DATABASE_URI)

    elif args.mode == "update":
        update_location_coordinates(DATABASE_URI)


if __name__ == "__main__":
    main()
