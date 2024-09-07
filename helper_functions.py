import pycountry
import requests
from datetime import datetime


def timestamp_to_date(timestamp: str) -> str:
    """
    Converts a timestamp in the format 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS.SSS'
    or 'YYYY-MM-DDTHH:MM:SS.SSSSSS' to a date 'YYYY-MM-DD'.

    Parameters:
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

    Parameters:
        date_str (str): The date string to be converted.
        input_format (str): The format of the input date string.
        output_format (str): The desired format for the output date string.

    Returns:
        str: The date string in the desired output format.
    """
    date_obj = datetime.strptime(date_str, input_format)
    formatted_date = date_obj.strftime(output_format)

    return formatted_date


def country_to_iso_codes(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2, country.alpha_3
    except LookupError:
        return None, None



