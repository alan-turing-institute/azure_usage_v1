"""
test functions to handle subscriptions

Author: Tomas Lazauskas
"""

import pytest
import os
import pandas as pd
from math import pi

from ..src_webapp.subs import (
    get_data_for_subid,
    get_top_services,
    calc_top_services_perc
)

from ..src_webapp.constants import (
    CONST_TEST_DIR_DATA_LOADER,
    CONST_TEST_DIR_0,
    CONST_TEST_DIR_1,
    CONST_TEST_DIR_4,
    CONST_TEST_DIR_6,
    CONST_TEST_DIR_1_SUB_ID_1,
    CONST_TEST_DIR_1_SUB_ID_2,
    CONST_COL_NAME_COST,
    CONST_COL_NAME_SERVICETYPE,
    CONST_COL_NAME_SERVICE,
    CONST_COL_NAME_ANGLE,
    CONST_MAX_TOP_SERVICES,
    CONST_NAME_OTHER,
    CONST_COL_NAME_PERC,
    CONST_RB_VALUE_0,
    CONST_RB_VALUE_1,
    CONST_RB_VALUE_2,
    CONST_RB_VALUE_3
)

from ..src_webapp.utilities import prep_sub_ids

from ..src_webapp.data_loader import create_dataframe

def test_get_data_for_subid():

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_1)
    raw_usage = create_dataframe(data_path)

    sub_ids = prep_sub_ids(CONST_TEST_DIR_1_SUB_ID_1)
    result = get_data_for_subid(raw_usage, sub_ids)
    assert (len(result.index) == 15)

    sub_ids = prep_sub_ids(CONST_TEST_DIR_1_SUB_ID_1 + "," + CONST_TEST_DIR_1_SUB_ID_2)
    result = get_data_for_subid(raw_usage, sub_ids)
    assert (len(result.index) == 29)

    sub_ids = prep_sub_ids(None)
    result = get_data_for_subid(raw_usage, sub_ids)
    assert (result.empty)
 
    sub_ids = prep_sub_ids("")
    result = get_data_for_subid(raw_usage, sub_ids)
    assert (result.empty)

    sub_ids = prep_sub_ids("abc")
    result = get_data_for_subid(raw_usage, sub_ids)
    assert (result.empty)

    sub_ids = prep_sub_ids("abc,xxx")
    result = get_data_for_subid(raw_usage, sub_ids)
    assert (result.empty)

def test_get_top_services_grouping():
    # Checking simple grouping by top services
    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_1)
    raw_usage = create_dataframe(data_path)
    
    # checking grouping 0
    top_services = get_top_services(raw_usage, top_services_num=20, top_services_grp_md=CONST_RB_VALUE_0)

    value = round(float(top_services[top_services[CONST_COL_NAME_SERVICE] == "BASIC.A0 VM"][CONST_COL_NAME_COST]), 10)
    assert(value == 1.995901038)
    
    # checking the number of top services
    assert (len(top_services.index) == 6)

    # checking grouping 1
    top_services = get_top_services(raw_usage, top_services_num=20, top_services_grp_md=CONST_RB_VALUE_1)

    # checking the value of one of the top services    
    value = round(float(top_services[top_services[CONST_COL_NAME_SERVICE] == "Virtual Machines: BASIC.A0 VM: Compute Hours"][CONST_COL_NAME_COST]), 10)
    assert(value == 1.995901038)

    # checking the number of top services
    assert (len(top_services.index) == 17)

    # checking grouping 2
    top_services = get_top_services(raw_usage, top_services_num=20, top_services_grp_md=CONST_RB_VALUE_2)

    value = round(float(top_services[top_services[CONST_COL_NAME_SERVICE] == "Virtual Machines: BASIC.A0 VM"][CONST_COL_NAME_COST]), 10)
    assert(value == 1.995901038)
    
    # checking the number of top services
    assert (len(top_services.index) == 7)

    # checking grouping 3
    top_services = get_top_services(raw_usage, top_services_num=20, top_services_grp_md=CONST_RB_VALUE_3)

    print(top_services)

    value = round(float(top_services[top_services[CONST_COL_NAME_SERVICE] == "Virtual Machines: Compute Hours"][CONST_COL_NAME_COST]), 10)
    assert(value == 2.289601566)
    
    # checking the number of top services
    assert (len(top_services.index) == 16)

def test_get_top_services():
    
    # Checking simple grouping by top services
    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_1)
    raw_usage = create_dataframe(data_path)
    
    top_services = get_top_services(raw_usage, top_services_num=20)

    # checking the total cost
    assert (round(top_services[CONST_COL_NAME_COST].sum(), 10) == 169.611998454)

    # checking what happens when we pass an empty dataframe with structure
    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_4)
    raw_usage = create_dataframe(data_path)

    top_services = get_top_services(raw_usage, top_services_grp_md=CONST_RB_VALUE_1)

    assert(top_services.empty)

    # checking what happens if we pass an empty dataframe object
    top_services = get_top_services(pd.DataFrame())
    
    assert(top_services == None)

    # checking what happens when we pass None
    top_services = get_top_services(None)

    assert(top_services == None)

    # test the maximum number of top services
    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_6)
    raw_usage = create_dataframe(data_path)
    top_services = get_top_services(raw_usage, top_services_num=10, top_services_grp_md=CONST_RB_VALUE_1)
    
    # checking the number of top services (+1 for the "other" line)
    assert (len(top_services.index) == 11)

    # checking the value of the other type 
 
    value = float(top_services.loc[top_services[CONST_COL_NAME_SERVICE].str.startswith(CONST_NAME_OTHER), CONST_COL_NAME_COST])
    assert(value == 3000)

    # checking the total cost
    assert (top_services[CONST_COL_NAME_COST].sum() == 78000)

    # checking percentage
    value = float(top_services.loc[top_services[CONST_COL_NAME_SERVICE].str.startswith(CONST_NAME_OTHER), CONST_COL_NAME_PERC])
    assert(value == 0.038461538461538464)

def test_calc_top_services_perc():

    # Checking simple grouping by top services
    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_1)
    raw_usage = create_dataframe(data_path)
    
    top_services = get_top_services(raw_usage, top_services_num=20)

    # calculate percentages for the top services
    top_services = calc_top_services_perc(top_services)

    # Angles should sum up to 2 PI
    test_value = 2 * pi
    assert(round(top_services[CONST_COL_NAME_ANGLE].sum(), 13) == round(test_value, 13))
