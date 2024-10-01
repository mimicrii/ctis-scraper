from typing import Tuple
import pycountry
import requests
from datetime import datetime
from dataclasses import dataclass


def timestamp_to_date(timestamp: str) -> str:
    """
    Converts a timestamp in the format 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS.SSS'
    or 'YYYY-MM-DDTHH:MM:SS.SSSSSS' to a date 'YYYY-MM-DD'.

    Parameter:
        timestamp (str): The timestamp string to be converted.

    Returns:
        str: The date string in 'YYYY-MM-DD' format.
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

    date_str = dt.strftime("%Y-%m-%d")
    return date_str


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

    return formatted_date


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
    try:
        response.raise_for_status()
        json_data = response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.content}")
        raise
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        raise
    except ValueError as json_err:
        print(f"JSON decoding failed: {json_err}")
        print(f"Response content: {response.content}")
        raise
    return json_data



