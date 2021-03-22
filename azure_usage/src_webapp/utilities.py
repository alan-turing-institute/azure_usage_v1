"""
Utilities module
"""

import os
import pandas as pd

from .constants import (
    URL_PARAM_SUB_IDS,
    URL_PARAM_REPORT,
    URL_PARAM_DT_FROM,
    URL_PARAM_DT_TO,
    DEFAULT_REPORT_NAME,
    CONST_ENCODING,
)


def prep_sub_id(sub_id_input):
    """Processes subscription ID

    Args:
        sub_id_input: raw subscription id
    Returns:
        Processed subscription id

    """

    if not isinstance(sub_id_input, str):
        return ""

    if len(sub_id_input) == 0:
        return ""

    return "{" + sub_id_input.strip().upper() + "}"


def prep_sub_ids(sub_ids_input):
    """Processes subscription IDs to be used for selecting data

    Args:
        sub_ids_input: raw string containing subscription ids
        separated via comma

    Returns:
        a processed subscription id or a list of processed subscription ids
    """

    if not isinstance(sub_ids_input, str):
        return ""

    if len(sub_ids_input) == 0:
        return ""

    sub_id_array = sub_ids_input.split(",")

    if len(sub_id_array) == 0:
        return ""

    sub_ids_list = []

    for sub_id in sub_id_array:
        sub_ids_list.append(prep_sub_id(sub_id))

    return sub_ids_list


def diff_month(date1, date2):
    """Counts the number of months between two dates

    Args:
        d1 - date to
        d2 - date from
    Returns:
        number of months between two dates
    """

    return (date1.year - date2.year) * 12 + date1.month - date2.month


def parse_url_params(url_params):
    """Reads in url parameters.

    Arguments:
        url_params: arguments of a bokeh document

    Returns:
        A dictionary with the parsed url parameters
    """

    if URL_PARAM_SUB_IDS in url_params:

        sub_ids = url_params[URL_PARAM_SUB_IDS][0].decode(CONST_ENCODING)

        if sub_ids in [None, "None"]:
            sub_ids = ""

    else:
        sub_ids = ""

    if URL_PARAM_REPORT in url_params:
        report_title = url_params[URL_PARAM_REPORT][0].decode(CONST_ENCODING)

        if report_title in [None, "None"]:
            report_title = DEFAULT_REPORT_NAME

    else:
        report_title = DEFAULT_REPORT_NAME

    # Initialise date range min and max to None so we can tell if they've
    # been set from the URL
    date_min = None
    date_max = None

    # Read min and max date ranges from URL query parameters if present
    if URL_PARAM_DT_FROM in url_params:
        try:
            date_from_text = url_params[URL_PARAM_DT_FROM][0].decode(
                CONST_ENCODING
            )
            date_min = pd.to_datetime(date_from_text, format="%Y-%m-%d")
        except ValueError:
            pass
    if URL_PARAM_DT_TO in url_params:
        try:
            date_from_text = url_params[URL_PARAM_DT_TO][0].decode(
                CONST_ENCODING
            )
            date_max = pd.to_datetime(date_from_text, format="%Y-%m-%d")
        except ValueError:
            pass

    url_params = dict()

    url_params[URL_PARAM_REPORT] = report_title
    url_params[URL_PARAM_SUB_IDS] = sub_ids
    url_params[URL_PARAM_DT_FROM] = date_min
    url_params[URL_PARAM_DT_TO] = date_max

    return url_params


def read_timestamp(timestamp_path):
    """
    Reads in timestamp file when the last time data was updated.

    Args:
        timestamp_path - full path to the timestamp file
    Returns:
        Time stamp in pandas datetime format

    """

    try:
        timestamp_f = open(os.path.abspath(timestamp_path), "r")
        file_context = timestamp_f.read().replace("\n", "")
        timestamp_f.close()
        result = pd.to_datetime(file_context)
        return result
    except Exception:
        return None
