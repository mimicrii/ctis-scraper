import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from api import get_trial_overview, get_trial_details
from crud import insert_trial_data, update_location_coordinates
from schemas import Base


def main():
    load_dotenv()
    DATABASE_URI = os.getenv("DATABASE_URI")

    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(engine)
    if len(sys.argv) < 2:
        print("Enter an argument")
        exit()

    match sys.argv[1]:
        case "scrape_all":
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            with Session() as session:
                for trial_overview in get_trial_overview():
                    trial_details = get_trial_details(trial_overview["ctNumber"])
                    insert_trial_data(
                        session=session,
                        trial_overview=trial_overview,
                        trial_details=trial_details,
                    )

        case "update_coordinates":
            with Session() as session:
                update_location_coordinates(session)

        case _:
            print("Invalid argument")


if __name__ == "__main__":
    main()
