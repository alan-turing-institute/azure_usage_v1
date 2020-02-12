"""
test utilities

Author: Tomas Lazauskas
"""

import pytest
import pandas as pd
import os

from ..src_webapp.utilities import (
    prep_sub_id,
    prep_sub_ids,
    diff_month,
    parse_url_params,
    read_timestamp)

from ..src_webapp.constants import (
    URL_PARAM_SUB_IDS,
    URL_PARAM_REPORT,
    URL_PARAM_DT_FROM,
    URL_PARAM_DT_TO,
    DEFAULT_REPORT_NAME,
    CONST_ENCODING,
    CONST_TEST_DIR_DATA_LOADER,
    TIMESTAMP_FILE
)

def test_prep_sub_id():
    """
    Testing parsing single subid
    """

    result = prep_sub_id(None)
    assert(result == "")

    result = prep_sub_id("")
    assert(result == "")

    result = prep_sub_id("abC")
    assert(result == "{ABC}")

def test_prep_sub_ids():
    """
    Testing parsing multiple subids

    """

    result = prep_sub_ids(None)
    assert(result == "")

    result = prep_sub_ids("")
    assert(result == "")

    result = prep_sub_ids("a,b")
    assert(result == ['{A}', '{B}'])

def test_diff_month():
    """
    Testing the function counting difference in months
    """

    dt_to = pd.to_datetime("2020-04-01")
    dt_from = pd.to_datetime("2019-01-01")
    result = diff_month(dt_to, dt_from)
    assert(result == 15)

    dt_to = pd.to_datetime("2019-01-01")
    dt_from = pd.to_datetime("2019-01-01")
    result = diff_month(dt_to, dt_from)
    assert(result == 0)

    dt_to = pd.to_datetime("2018-01-01")
    dt_from = pd.to_datetime("2019-01-01")
    result = diff_month(dt_to, dt_from)
    assert(result == -12)

def test_parse_url_params():

    # Simple test
    test_repor_title = b"Tomas L test"
    test_sub_id = b'F4A7612B-288E-4F5D-A33A-A8C18E9E875C'
    test_date_from = b'2019-10-03'
    test_date_to = b'2019-10-24'

    test_object = {'bokeh-autoload-element': [b'1002'], 
        'bokeh-app-path': [b'/bokeh_server'], 
        'bokeh-absolute-url': [b'http://0.0.0.0:5006/bokeh_server'], 
        URL_PARAM_REPORT: [test_repor_title], 
        URL_PARAM_SUB_IDS: [test_sub_id], 
        URL_PARAM_DT_FROM: [test_date_from], 
        URL_PARAM_DT_TO: [test_date_to]}

    result_dict = parse_url_params(test_object)

    assert(result_dict[URL_PARAM_REPORT] == test_repor_title.decode(CONST_ENCODING))
    assert(result_dict[URL_PARAM_SUB_IDS] == test_sub_id.decode(CONST_ENCODING))
    assert(result_dict[URL_PARAM_DT_FROM] == pd.to_datetime(test_date_from.decode(CONST_ENCODING), format='%Y-%m-%d'))
    assert(result_dict[URL_PARAM_DT_TO] == pd.to_datetime(test_date_to.decode(CONST_ENCODING), format='%Y-%m-%d'))

    # Empty test
    test_object = {}
    result_dict = parse_url_params(test_object)

    assert(result_dict[URL_PARAM_REPORT] == DEFAULT_REPORT_NAME)
    assert(result_dict[URL_PARAM_SUB_IDS] == '')
    assert(result_dict[URL_PARAM_DT_FROM] == None)
    assert(result_dict[URL_PARAM_DT_TO] == None)

    # Wrong dates test
    test_date_from_2 = b'2019-13-03'
    test_object = {
        URL_PARAM_DT_FROM: [test_date_from_2],
        URL_PARAM_DT_TO: [test_date_from_2]}

    result_dict = parse_url_params(test_object)

    assert(result_dict[URL_PARAM_DT_FROM] == None)
    assert(result_dict[URL_PARAM_DT_TO] == None)

def test_read_timestamp():

    path_to_timestamp = os.path.join(CONST_TEST_DIR_DATA_LOADER, TIMESTAMP_FILE)
    result = read_timestamp(path_to_timestamp)
    assert(result == pd.to_datetime('2019-12-12 15:49:30.988079'))

    path_to_timestamp = os.path.join(CONST_TEST_DIR_DATA_LOADER, "doesnt_exist.txt")
    result = read_timestamp(path_to_timestamp)
    assert(result == None)
