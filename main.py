import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from tqdm import tqdm

from schemas import Base
from api import get_trial_overview, get_trial_details, get_total_trial_records
from crud import (
    delete_table_entries,
    insert_trial_data,
    update_location_coordinates,
    insert_update_status,
)


def main():
    load_dotenv()  # load dotenv when testing locally
    DATABASE_URI = os.getenv("DATABASE_URI")
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(engine)
    total_trial_records = get_total_trial_records()

    if len(sys.argv) < 2:
        print("Enter an argument")
        exit()

    match sys.argv[1]:
        case "scrape":
            with Session() as session:
                try:
                    delete_table_entries(
                        session=session,
                        delete_all_except=True,
                        table_names=["location", "update_history"],
                    )
                    session.commit()  # TODO: Do not commit here to keep whole process in one transaction
                    Base.metadata.create_all(engine)

                    print("Scraping trial data...")
                    for trial_overview in tqdm(
                        get_trial_overview(), total=total_trial_records
                    ):
                        trial_details = get_trial_details(trial_overview["ctNumber"])
                        insert_trial_data(
                            session=session,
                            trial_overview=trial_overview,
                            trial_details=trial_details,
                        )

                    session.commit()
                    insert_update_status(session, "Update successful")

                except Exception as e:
                    session.rollback()
                    insert_update_status(session, f"Update failed - {type(e).__name__}")
                    raise

        case "update_coordinates":
            with Session() as session:
                update_location_coordinates(session)

        case _:
            print("Invalid argument")


if __name__ == "__main__":
    main()
