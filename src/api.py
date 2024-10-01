import requests
import json
import yaml
from typing import Iterator, Tuple, Final
from dataclasses import dataclass

from src.helpers import convert_date_format, validate_response
from src.parse import TrialOverview

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

OVERVIEW_PAYLOAD: dict = config["api"]["overview"]["payload"]
OVERVIEW_URL: Final[str] = "https://euclinicaltrials.eu/ctis-public-api/search"
OVERVIEW_HEADERS: Final[str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Origin": "https://euclinicaltrials.eu",
    "Connection": "keep-alive",
    "Referer": "https://euclinicaltrials.eu/ctis-public/search?lang=en",
}
GEOCODING_URL: Final[str] = f"https://nominatim.openstreetmap.org/search"
GEOCODING_HEADERS: dict = config["api"]["geocoding"]["headers"]


def get_trial_overview() -> Iterator[TrialOverview]:
    """
    Generate a generator that yields trial overviews.

    This function paginates through the API results, processing each page
    and yielding individual trial overviews. Handles pagination by
    incrementing the page number and checking for the availability of
    the next page.

    Yields:
        dataclass: Instance of TrialOverview containing trial overview data parsed from response json
    """
    next_page_available = True
    page = 1
    payload = OVERVIEW_PAYLOAD

    while next_page_available:
        payload["pagination"]["page"] = page
        r = requests.post(
            OVERVIEW_URL, headers=OVERVIEW_HEADERS, data=json.dumps(payload)
        )
        json_data = validate_response(r)
        for trial in json_data["data"]:
            trial_overview = TrialOverview(**trial)
            yield trial_overview

        page += 1
        next_page_available = json_data["pagination"]["nextPage"]


def get_total_trial_records() -> int:
    """
    Uses the overview api endpoint to return the total number of trials currently available.
    """
    r = requests.post(
        OVERVIEW_URL, headers=OVERVIEW_HEADERS, data=json.dumps(OVERVIEW_PAYLOAD)
    )
    json_data = validate_response(r)
    total_trials = json_data.get("pagination").get("totalRecords")
    return total_trials


def get_trial_details(ct_number: str) -> dict:
    """
    Return the response with trial details of a single trial.

    Parameter:
    - ct_number: The ct number identifier of a trial listed in the ctis portal.
    """
    details_url = f"https://euclinicaltrials.eu/ctis-public-api/retrieve/{ct_number}"
    r = requests.get(details_url)
    json_data = validate_response(r)
    return json_data


def get_location_coordinates(
    street: str, city: str, country: str, postalcode: str
) -> Tuple[int, int]:
    """
    Uses the Nomatim geocoding api to get lat and lon coordinates for provided address information

    Parameter:
    - street: Location street
    - city: Location city
    - country: Location country
    - postalcode: Location postalcode
    """

    params = {
        "street": street,
        "city": city,
        "postalcode": postalcode,
        "country": country,
        "format": "json",
        "limit": "1",
    }

    r = requests.get(GEOCODING_URL, params=params, headers=GEOCODING_HEADERS)
    json_data = validate_response(r)

    if len(json_data) == 0:
        print(f"No coordinates found for {street}, {city}, {country}")
        return None, None

    lat = json_data[0]["lat"]
    lon = json_data[0]["lon"]
    return lat, lon
