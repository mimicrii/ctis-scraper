import os
from datetime import datetime
from dataclasses import dataclass
from typing import Tuple

import pycountry
import requests
import yaml
from dotenv import load_dotenv

from src.log import logger
from src.parse import SponsorDuty


def get_db_uri() -> str:
    """
    Checks config file for selected environment and returns matching database uri.

    Returns:
    - Environment is set to produktive ("prod"): Database uri provided as an env variable
    - Environment is set to development ("dev"): Sqlite database uri for development database.
    """
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    environment = config["environment"]

    if environment == "prod":
        load_dotenv()  # load dotenv when running locally
        database_uri = os.getenv("DATABASE_URI")
    elif environment == "dev":
        database_uri = "sqlite:///dev.db"
    else:
        raise ValueError(
            f"Wrong environment configuration ({environment}). Choose either 'dev' or 'prod'"
        )
    return database_uri


def timestamp_to_date(timestamp: str) -> datetime.date:
    """
    Converts a timestamp in the format 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS.SSS'
    or 'YYYY-MM-DDTHH:MM:SS.SSSSSS' to a python date object.

    Parameter:
        timestamp (str): The timestamp string to be converted.

    Returns:
        datetime.date: A python date object.
    """
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise ValueError(
                "Timestamp format is incorrect. Ensure it's in the form 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS.SSS'."
            )

    return dt.date()


def convert_date_format(date_str: str, input_format: str, output_format: str) -> str:
    """
    Converts a date string from the input format to the desired output format.

    Parameter:
        date_str (str): The date string to be converted.
        input_format (str): The format of the input date string.
        output_format (str): The desired format for the output date string.

    Returns:
        str: The date string in the desired output format.
    """
    date_obj = datetime.strptime(date_str, input_format)
    formatted_date = date_obj.strftime(output_format)

    return date_obj.date()


def country_to_iso_codes(country_name: str) -> Tuple[str, str]:
    """
    Converts the name of a country to its corresponding ISO2 and ISO3 codes.
    """

    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2, country.alpha_3
    except LookupError:
        return None, None


def validate_response(response: requests.Response) -> dict:
    """
    Validates a json response by checking for http status and validity of the json content.

    Parameter:
    - response (requests.Response): An instance of the Response class.

    Returns:
    - dict: The validated json content
    """

    try:
        response.raise_for_status()
        json_data = response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        logger.info(f"Response content: {response.content}")
        raise
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        raise
    except ValueError as json_err:
        logger.error(f"JSON decoding failed: {json_err}")
        logger.info(f"Response content: {response.content}")
        raise
    return json_data


def decode_third_party_duty(duty: SponsorDuty, decodings: dict) -> str:
    """
    Checks if duty value is provided in response and returns it. If not returns value decoded with decoding dict.

    Parameter:
    - duty (SponsorDuty): Instance of SponsorDuty dataclass
    - decodings (dict): Decodings of duty codes into actual values

    Returns:
    - str: Decoded duty value
    """

    duty_code = duty.code
    duty_value = duty.value
    if duty_value:
        return duty_value
    else:
        return decodings[duty_code]
