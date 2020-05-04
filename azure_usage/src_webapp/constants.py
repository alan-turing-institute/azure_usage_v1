#!/usr/bin/env python
# encoding: utf-8

"""
constants.py
"""

import os

CONST_MAX_TOP_SERVICES = 19
CONST_MAX_SERVICE_LENGTH = 50
CONST_NONE = "---"

URL_PARAM_REPORT = "report_title"
URL_PARAM_SUB_IDS = "subscription_ids"
URL_PARAM_DT_FROM = "date_from"
URL_PARAM_DT_TO = "date_to"

DATA_DT_FROM = "date_from"
DATA_DT_TO = "date_to"

README_FILE = "README.md"
UPDATES_FILE = "UPDATES.txt"
TIMESTAMP_FILE = "update.log"
DATA_FOLDER = "data"
CONST_TEST_FOLDER = "tests"

DEFAULT_REPORT_NAME = "Azure usage analysis"

CONST_COL_NAME_QUANTITY = "Quantity"
CONST_COL_NAME_COST = "Cost"
CONST_COL_NAME_SOURCEFILE = "SourceFile"
CONST_COL_NAME_DATE = "Date"
CONST_COL_NAME_SGUID = "SubscriptionGuid"
CONST_COL_NAME_SNAME = "SubscriptionName"
CONST_COL_NAME_YM = "Year-Month"
CONST_COL_NAME_SERVICETYPE = "ServiceType"
CONST_COL_NAME_SERVICENAME = "ServiceName"
CONST_COL_NAME_SERVICERESOURCE = "ServiceResource"
CONST_COL_NAME_SUM = "sum"
CONST_COL_NAME_PERC = "Perc"
CONST_COL_NAME_SERVICE = "Service"
CONST_COL_NAME_ANGLE = "angle"
CONST_COL_NAME_IDEALCOST = "Ideal_Cost"
CONST_COL_NAME_AVAILCOST = "Avail_Cost"
CONST_COL_NAME_SUB = "Subscription"

CONST_COL_NAME_HANDOUTNAME = "HandoutName"
CONST_COL_NAME_LABNAME = "LabName"
CONST_COL_NAME_COURSENAME = "CourseName"

CONST_NAME_OTHER = "Other"

CONST_TEST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", CONST_TEST_FOLDER)
)

CONST_TEST_DIR_DATA_LOADER = os.path.join(CONST_TEST_DIR, DATA_FOLDER)
CONST_TEST_DIR_0 = "0_empty_dir"
CONST_TEST_DIR_1 = "1_one_file"
CONST_TEST_DIR_1_SUB_ID_1 = "B74C2AF1-7411-46FC-9A36-4C6E384DB6EA"
CONST_TEST_DIR_1_SUB_ID_2 = "9A2EE171-E59B-49A1-A68C-3ED2E9A04ED9"
CONST_TEST_DIR_2 = "2_no_dir"
CONST_TEST_DIR_3 = "3_multiple_files"
CONST_TEST_DIR_4 = "4_empty_file"
CONST_TEST_DIR_5 = "5_missing_days"
CONST_TEST_DIR_6 = "6_multiple_services"
CONST_TEST_DIR_8 = "8_eduhub"

CONST_RB_DEFAULT = 0
CONST_RB_LABEL_0 = "Type"
CONST_RB_VALUE_0 = 0
CONST_RB_LABEL_1 = "Name + Type + Resource"
CONST_RB_VALUE_1 = 1
CONST_RB_LABEL_2 = "Name + Type"
CONST_RB_VALUE_2 = 2
CONST_RB_LABEL_3 = "Name + Resource"
CONST_RB_VALUE_3 = 3

CONST_ENCODING = "utf-8"
