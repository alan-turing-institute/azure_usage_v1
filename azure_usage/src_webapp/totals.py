#!/usr/bin/python
"""
Python module to perform operations related to aggregated numbers.
"""

import pandas as pd

from dateutil.relativedelta import relativedelta

from .constants import (
    CONST_COL_NAME_SGUID,
    CONST_COL_NAME_YM,
    CONST_COL_NAME_DATE,
    CONST_COL_NAME_COST,
)


def group_day(raw_data, add_missing_days=False):
    """Groups raw usage by calender day

    Args:
        raw_data: raw usage data framework
        add_missing_days: flag to add missing days with Cost = 0
    Returns:
        raw_data_gr: dataframe of grouped raw usage by calender day
    """

    raw_data_ = raw_data.copy()

    raw_data_gr = (
        raw_data_.groupby([CONST_COL_NAME_DATE])[CONST_COL_NAME_COST]
        .sum()
        .reset_index()
        .sort_values(by=[CONST_COL_NAME_DATE], ascending=True)
    )

    if add_missing_days:
        raw_data_gr.set_index(CONST_COL_NAME_DATE, inplace=True)
        raw_data_gr = (
            raw_data_gr.resample("D").asfreq().fillna(0).reset_index()
        )

    raw_data_gr["Date"] = pd.to_datetime(raw_data_gr["Date"])

    raw_data_gr["Date_str"] = raw_data_gr["Date"].dt.strftime("%Y-%m-%d")

    # raw_data_gr['Date_id'] = [x for x in range(raw_data_gr.shape[0])]

    raw_data_gr.reset_index(drop=True, inplace=True)

    return raw_data_gr


def add_missing_year_months(df, date_from, date_to, value_col_name):
    """
    Adds missing Year-Month values from the given range to the
        dataframe with zero values in the specified column

    Args:
        df - dataframe of grouped raw usage by calender month
        date_from - analysis period start date
        date_to - analysis period end date
        value_col_name - costs column name

    Returns:
        df - appended dataframe
    """

    cur_date = date_from

    while cur_date < date_to:
        year_month = "{year}-{month:02d}".format(
            year=cur_date.year, month=cur_date.month
        )
        cur_date += relativedelta(months=1)

        if year_month not in df[CONST_COL_NAME_YM].values:
            df = df.append(
                {CONST_COL_NAME_YM: year_month, value_col_name: 0.0},
                ignore_index=True,
            )

    return df


def group_year_month(raw_data):
    """Groups raw usage by calender month

    Args:
        raw_data: raw usage data framework
    Returns:
        raw_data_gr: dataframe of grouped raw usage by calender month
    """

    raw_data_ = raw_data.copy()
    raw_data_[CONST_COL_NAME_YM] = pd.to_datetime(
        raw_data_[CONST_COL_NAME_DATE]
    ).apply(lambda x: "{year}-{month:02d}".format(year=x.year, month=x.month))

    raw_data_gr = (
        raw_data_.groupby([CONST_COL_NAME_YM])[CONST_COL_NAME_COST]
        .sum()
        .reset_index()
        .sort_values(by=[CONST_COL_NAME_YM], ascending=True)
    )

    return raw_data_gr


def group_sub_year_month(raw_data):
    """Groups raw usage by calender month and subscriptionid

    Args:
        raw_data: raw usage data framework
    Returns:
        raw_data_gr: dataframe of grouped raw usage by calender month
    """

    raw_data_ = raw_data.copy()
    raw_data_[CONST_COL_NAME_YM] = pd.to_datetime(
        raw_data_[CONST_COL_NAME_DATE]
    ).apply(lambda x: "{year}-{month:02d}".format(year=x.year, month=x.month))

    raw_data_gr = (
        raw_data_.groupby([CONST_COL_NAME_SGUID, CONST_COL_NAME_YM])[
            CONST_COL_NAME_COST
        ]
        .sum()
        .reset_index()
        .sort_values(by=[CONST_COL_NAME_YM], ascending=True)
    )

    return raw_data_gr
