"""
test totals

Author: Tomas Lazauskas
"""

import pytest
import os
import pandas as pd

from ..src_webapp.totals import (
    group_day,
    group_year_month,
    group_sub_year_month
)

from ..src_webapp.data_loader import create_dataframe

from ..src_webapp.constants import (
    CONST_COL_NAME_COST,
    CONST_COL_NAME_DATE,
    CONST_COL_NAME_SGUID,
    CONST_COL_NAME_YM,
    CONST_TEST_DIR_DATA_LOADER,
    CONST_TEST_DIR_1,
    CONST_TEST_DIR_5,
    CONST_TEST_DIR_1_SUB_ID_1,
    CONST_TEST_DIR_1_SUB_ID_2
)

def test_group_day():

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_5)
    raw_usage = create_dataframe(data_path)

    dt_to = pd.to_datetime("2019-08-01")
    dt_from = pd.to_datetime("2018-10-11")

    raw_usage = raw_usage[(raw_usage[CONST_COL_NAME_DATE]>=dt_from) & (raw_usage[CONST_COL_NAME_DATE]<=dt_to)]

    result = group_day(raw_usage)
    assert (len(result.index) == 199)
    assert (round(result[CONST_COL_NAME_COST].sum(), 10) == 1097.9489568535)
    
    result = group_day(raw_usage, add_missing_days=True)
    assert (len(result.index) == 295)
    assert (round(result[CONST_COL_NAME_COST].sum(), 10) == 1097.9489568535)

def test_group_year_month():

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_5)
    raw_usage = create_dataframe(data_path)

    dt_to = pd.to_datetime("2019-08-01")
    dt_from = pd.to_datetime("2018-10-11")

    raw_usage = raw_usage[(raw_usage[CONST_COL_NAME_DATE]>=dt_from) & (raw_usage[CONST_COL_NAME_DATE]<=dt_to)]

    result = group_year_month(raw_usage)
    assert (round(result[CONST_COL_NAME_COST].sum(), 10) == 1097.9489568535) 
    assert (len(result.index) == 11)

    assert(round(float(result[result[CONST_COL_NAME_YM]=="2019-07"][CONST_COL_NAME_COST]), 10) == 70.451235495)

def test_group_sub_year_month():

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_5)
    raw_usage = create_dataframe(data_path)

    dt_to = pd.to_datetime("2019-08-01")
    dt_from = pd.to_datetime("2018-10-11")

    raw_usage = raw_usage[(raw_usage[CONST_COL_NAME_DATE]>=dt_from) & (raw_usage[CONST_COL_NAME_DATE]<=dt_to)]

    result = group_sub_year_month(raw_usage)

    assert (round(result[CONST_COL_NAME_COST].sum(), 10) == 1097.9489568535) 
    assert (len(result.index) == 11)
    assert(round(float(result[result[CONST_COL_NAME_YM]=="2019-07"][CONST_COL_NAME_COST]), 10) == 70.451235495)

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_1)
    raw_usage = create_dataframe(data_path)
    
    result = group_sub_year_month(raw_usage)
  
    assert(round(float(result[(result[CONST_COL_NAME_YM]=="2016-10") & (result[CONST_COL_NAME_SGUID]=="{" + CONST_TEST_DIR_1_SUB_ID_1 + "}")][CONST_COL_NAME_COST]), 10) == 0.78794627)
    assert(round(float(result[(result[CONST_COL_NAME_YM]=="2016-10") & (result[CONST_COL_NAME_SGUID]=="{" + CONST_TEST_DIR_1_SUB_ID_2 + "}")][CONST_COL_NAME_COST]), 10) == 168.824052184)
