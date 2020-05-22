"""
test data import functions

Author: Tomas Lazauskas
"""

import os
import datetime

from ..src_webapp.constants import (
    CONST_COL_NAME_QUANTITY,
    CONST_COL_NAME_COST,
    CONST_TEST_DIR_DATA_LOADER,
    CONST_TEST_DIR_0,
    CONST_TEST_DIR_1,
    CONST_TEST_DIR_2,
    CONST_TEST_DIR_3,
    CONST_TEST_DIR_4,
    CONST_TEST_DIR_8,
)
from ..src_webapp.data_loader import create_dataframe, check_filename_convention


def test_check_filename_convention():
    """
    Testing filename convention checker
    """

    # Pass
    result, start_date, end_date = check_filename_convention(
        "2019-10-01-2019-09-15.csv"
    )
    assert result
    assert start_date == datetime.datetime(2019, 9, 15, 0, 0)
    assert end_date == datetime.datetime(2019, 10, 1, 0, 0)

    result, start_date, end_date = check_filename_convention(
        "EduHub_2019-10-01-2019-09-15.csv"
    )
    assert result
    assert start_date == datetime.datetime(2019, 9, 15, 0, 0)
    assert end_date == datetime.datetime(2019, 10, 1, 0, 0)

    result, start_date, end_date = check_filename_convention(
        "EDUHUB_2019-10-01-2019-09-15.csv"
    )
    assert result
    assert start_date == datetime.datetime(2019, 9, 15, 0, 0)
    assert end_date == datetime.datetime(2019, 10, 1, 0, 0)

    # Fails

    # Reversed dates
    result, _, _ = check_filename_convention("2019-09-15-2019-10-01.csv")
    assert not result

    # Wrong seperator
    result, _, _ = check_filename_convention("2019_10_01_2019_09_15.csv")
    assert not result

    # Wrong date format
    result, _, _ = check_filename_convention("01-10-2019-15-09-2019.csv")
    assert not result


def test_create_dataframe_empty_dir():
    """
    Testing the simplest import from an empty directory
    """

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_0)

    raw_usage = create_dataframe(data_path)

    assert raw_usage.empty


def test_create_dataframe_single_file():
    """
    Testing the simplest import from one file with no surprises
    """

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_1)

    raw_usage = create_dataframe(data_path)

    # counting the number of entries
    assert len(raw_usage.index) == 29

    # checking the total cost
    assert raw_usage[CONST_COL_NAME_COST].sum() == 169.611998454


def test_create_dataframe_no_dir():
    """
    Testing the simplest import from a directory that does not exist

    """

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_2)

    raw_usage = create_dataframe(data_path)

    assert raw_usage.empty


def test_create_dataframe_multiple_files():
    """
    Testing import from multiple files with overlaping data

    The third file should override the second file's entry and keep the first files data
    """

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_3)

    raw_usage = create_dataframe(data_path)

    # counting the number of entries
    assert len(raw_usage.index) == 3

    # checking the total quantity
    assert raw_usage[CONST_COL_NAME_QUANTITY].sum() == 5.5

    # checking the total cost
    assert raw_usage[CONST_COL_NAME_COST].sum() == 5.5


def test_create_dataframe_empty_file():
    """
    Testing the simplest import from one file with no data
    """

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_4)

    raw_usage = create_dataframe(data_path)

    # counting the number of entries
    assert raw_usage.empty


def test_on_eduhub_data():
    """
    Testing data import with EduHub data
    """

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_8)

    raw_usage = create_dataframe(data_path)

    assert raw_usage[CONST_COL_NAME_COST].sum() == 228.05678868340001
