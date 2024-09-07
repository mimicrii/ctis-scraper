import requests
from typing import Generator
from helper_functions import convert_date_format


def get_trial_overview() -> Generator:
    overview_url = "https://euclinicaltrials.eu/ctis-public-api/search"
    next_page_available = True
    page = 1
    ct_numbers_scraped = 0

    while next_page_available:
        search_params = {
            "pagination": {"page": page, "size": 250},
            "sort": {"property": "decisionDate", "direction": "DESC"},
            "searchCriteria": {"containAll": "", "containAny": "", "containNot": ""},
        }
        r = requests.post(overview_url, json=search_params)
        json_data = r.json()

        for trial in json_data["data"]:
            trial_overview = {}
            trial_overview["ctNumber"] = trial.get("ctNumber")
            trial_overview["ctTitle"] = trial.get("ctTitle")
            trial_overview["ctStatus"] = trial.get("ctStatus")
            trial_overview["trialPhase"] = trial.get("trialPhase")
            trial_overview["ageGroup"] = trial.get("ageGroup")
            trial_overview["gender"] = trial.get("gender")
            trial_overview["trialRegion"] = trial.get("trialRegion")
            trial_overview["totalNumbersEnrolled"] = trial.get("totalNumbersEnrolled")
            trial_overview["lastUpdated"] = convert_date_format(
                trial.get("lastUpdated"),
                input_format="%d/%m/%Y",
                output_format="%Y-%m-%d",
            )

            ct_numbers_scraped += 1
            print(trial_overview["ctNumber"])
            yield trial_overview

        page += 1
        next_page_available = json_data["pagination"]["nextPage"]


def get_trial_details(ct_number) -> dict:
    details_url = f"https://euclinicaltrials.eu/ctis-public-api/retrieve/{ct_number}"
    r = requests.get(details_url)
    return r.json()


def get_location_coordinates(street: str, city: str, country: str, postalcode: str):
    url = f"https://nominatim.openstreetmap.org/search"

    params = {
        "street": street,
        "city": city,
        "postalcode": postalcode,
        "country": country,
        "format": "json",
        "limit": "1",
    }
    headers = {"User-Agent": "clinicaltrial_sites/0.0.1"}

    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        json_data = r.json()

        if len(json_data) == 0:
            print(f"No coordinates found for {street}, {city}, {country}")
            return None, None

        lat = json_data[0]["lat"]
        lon = json_data[0]["lon"]
        return lat, lon

    if r.status_code == 403:
        print("BLOCKED")
        exit()
