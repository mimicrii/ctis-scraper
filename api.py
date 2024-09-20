import requests
import json
from typing import Generator
from helper_functions import convert_date_format

OVERVIEW_URL = "https://euclinicaltrials.eu/ctis-public-api/search"
OVERVIEW_PAYLOAD = {
    "pagination": {"page": 1, "size": 100},
    "sort": {"property": "decisionDate", "direction": "DESC"},
    "searchCriteria": {
        "containAll": None,
        "containAny": None,
        "containNot": None,
        "title": None,
        "number": None,
        "status": None,
        "medicalCondition": None,
        "sponsor": None,
        "endPoint": None,
        "productName": None,
        "productRole": None,
        "populationType": None,
        "orphanDesignation": None,
        "msc": None,
        "ageGroupCode": None,
        "therapeuticAreaCode": None,
        "trialPhaseCode": None,
        "sponsorTypeCode": None,
        "gender": None,
        "protocolCode": None,
        "rareDisease": None,
        "pip": None,
        "haveOrphanDesignation": None,
        "hasStudyResults": None,
        "hasClinicalStudyReport": None,
        "isLowIntervention": None,
        "hasSeriousBreach": None,
        "hasUnexpectedEvent": None,
        "hasUrgentSafetyMeasure": None,
        "isTransitioned": None,
        "eudraCtCode": None,
        "trialRegion": None,
        "vulnerablePopulation": None,
        "mscStatus": None,
    },
}
OVERVIEW_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Origin": "https://euclinicaltrials.eu",
    "Connection": "keep-alive",
    "Referer": "https://euclinicaltrials.eu/ctis-public/search?lang=en",
    "Cookie": "accepted_cookie=true",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "DNT": "1",
    "Sec-GPC": "1",
    "TE": "trailers",
}


def get_trial_overview() -> Generator:
    next_page_available = True
    page = 1
    payload = OVERVIEW_PAYLOAD

    while next_page_available:
        payload["pagination"]["page"] = page
        r = requests.post(
            OVERVIEW_URL, headers=OVERVIEW_HEADERS, data=json.dumps(payload)
        )
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
            yield trial_overview

        page += 1
        next_page_available = json_data["pagination"]["nextPage"]


def get_total_trial_records() -> int:
    r = requests.post(
        OVERVIEW_URL, headers=OVERVIEW_HEADERS, data=json.dumps(OVERVIEW_PAYLOAD)
    )
    json_data = r.json()
    total_trials = json_data.get("pagination").get("totalRecords")
    return total_trials


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
