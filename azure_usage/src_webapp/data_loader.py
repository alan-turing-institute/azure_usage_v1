#!/usr/bin/env python

"""
Functions to create dataframes from directories of Azure usage data.
Usage:
     create_dataframe_from_dir(<directory_name>)
         will create at a directory containing a self-consistent set of csv files.
     create_dataframe(<base_directory>)
         will loop through the subdirectories of a base directory, calling the above method on each,
         concatenating the dataframes and deduplicating (taking the last entry).
"""

import os
import datetime
import numpy as np
import pandas as pd

from .constants import (
    CONST_COL_NAME_QUANTITY,
    CONST_COL_NAME_COST,
    CONST_COL_NAME_SOURCEFILE,
    CONST_COL_NAME_DATE,
    CONST_COL_NAME_HANDOUTNAME,
    CONST_COL_NAME_LABNAME,
    CONST_COL_NAME_COURSENAME,
    CONST_COL_NAME_SNAME,
)


def check_filename_convention(filename):
    """
    Files should be named 'YYYY-MM-DD-YYY-MM-DD.csv' where the first date is
    the end of the time period and the second is the start of the time period.
    This checks for any dates named inconsistently.

    This will through an error if formatting is incorrect, and warn if the dates
    are not in the correct order.

    Returns True if format correct, False otherwise
    """

    if "eduhub" in filename.lower():
        filename = filename.lower().split("eduhub_")[1]

    filename = filename.replace(" ", "")

    end_date_str = filename[:10]
    start_date_str = filename[11 : 11 + 10]

    try:
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")

    except ValueError:
        start_date = None
        end_date = None

        print("File name {} has incorrect format".format(filename))
        return False, start_date, end_date

    if start_date >= end_date:
        print("File name {} has incorrect format".format(filename))
        return False, start_date, end_date

    return True, start_date, end_date


def create_dataframe_from_dir(directory):
    """
    Given a directory containing csv files, create a dataframe
    from each file, convert the 'Date' column to datetime, and concatenate.
    """

    if not os.path.exists(directory):
        return pd.DataFrame()

    file_list = os.listdir(directory)

    file_list.sort()

    df_list = []
    for filename in file_list:

        if filename.startswith("_") or (not filename.endswith(".csv")):
            continue

        # Assert that the file is named correctly
        _, start_date, end_date = check_filename_convention(filename)

        df = pd.read_csv(os.path.join(directory, filename))
        df = df.assign(SourceFile=filename)

        # In January 2020, MS changed the date format used in the usage 
        # export files from US to UK. This happen between 24/01/2020 - 
        # 28/01/2020. The following if statement is to deal with this
        # change.

        if start_date > datetime.datetime(2020, 1, 24, 0, 0):
            try:
                df[CONST_COL_NAME_DATE] = pd.to_datetime(
                    df[CONST_COL_NAME_DATE], format="%d/%m/%Y"
                )
            except:
                try:
                    df[CONST_COL_NAME_DATE] = pd.to_datetime(
                        df[CONST_COL_NAME_DATE], format="%m/%d/%Y"
                    )
                except:
                    df[CONST_COL_NAME_DATE] = pd.to_datetime(
                        df[CONST_COL_NAME_DATE], format="%Y-%m-%d"
                    )
        else:
            try:
                df[CONST_COL_NAME_DATE] = pd.to_datetime(
                    df[CONST_COL_NAME_DATE], format="%m/%d/%Y"
                )
            except:
                try:
                    df[CONST_COL_NAME_DATE] = pd.to_datetime(
                        df[CONST_COL_NAME_DATE], format="%d/%m/%Y"
                    )
                except:
                    df[CONST_COL_NAME_DATE] = pd.to_datetime(
                        df[CONST_COL_NAME_DATE], format="%Y-%m-%d"
                    )

        # Check if data comes from EduHub
        if CONST_COL_NAME_HANDOUTNAME in df.columns:

            # Renaming HandoutName to SubscriptionName
            df = df.rename(columns={CONST_COL_NAME_HANDOUTNAME: CONST_COL_NAME_SNAME})

            # Dropping columns CourseName,LabName
            df = df.drop(columns=[CONST_COL_NAME_LABNAME, CONST_COL_NAME_COURSENAME])

        df_list.append(df)

    if len(df_list) == 0:
        return pd.DataFrame()

    total_df = pd.concat(df_list, axis=0, ignore_index=True)

    return total_df


def concat_dataframes(df_list):
    """
    Takes a list of dataframes, concatenates them, and deduplicates based on
    all columns except for 'Quantity','Cost','SourceFile', taking the
    last entry (i.e. we assume that the dataframes are passed to it most-recent-last).
    """

    if len(df_list) == 0:
        return pd.DataFrame()

    total_df = pd.concat(df_list, axis=0, ignore_index=True)

    columns_to_dedup = list(total_df.columns)

    # if dataframe is empty and does not have any columns do not need to do anything
    if total_df.empty and (len(columns_to_dedup) == 0):
        return total_df

    columns_to_dedup.remove(CONST_COL_NAME_QUANTITY)
    columns_to_dedup.remove(CONST_COL_NAME_COST)
    columns_to_dedup.remove(CONST_COL_NAME_SOURCEFILE)

    return total_df.drop_duplicates(columns_to_dedup, keep="last")


def create_dataframe(base_dir):
    """
    Given a directory that contains some other directories (ideally ordered by date
    when sorted by name), loop through all these directories, create a data frame
    for each, and concatenate them using the concat_dataframes method (which will
    remove duplicates keeping the latest).
    """

    if not os.path.exists(base_dir):
        return pd.DataFrame()

    df_list = [
        create_dataframe_from_dir(os.path.join(base_dir, directory))
        for directory in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, directory))
    ]

    df_basedir = create_dataframe_from_dir(base_dir)
    if df_basedir is not None:
        df_list.append(df_basedir)

    final_df = concat_dataframes(df_list)

    return final_df


###### NO UNIT TESTS FOR ALL THE FOLLWING FUNCTIONS


def check_missing_data(df, date_from, date_to, ignore_from_today=True):
    """
    Check a dataframe for any missing days between date_from and data_to.
    Returns a list of dates that are missing
    If ignore_from_today dates from today onwards are not considered missing
    """

    unique_dates = pd.unique(df.Date)

    # Get the first date between date_to and today
    if ignore_from_today:
        date_to = np.min([date_to, pd.to_datetime(datetime.date.today())])

    date_range = np.arange(date_from, date_to, dtype="datetime64[D]").astype(
        "datetime64[ns]"
    )

    if unique_dates.dtype != date_range.dtype:
        raise TypeError("df does not contain the correct type")

    mask = list(map(lambda x: x not in unique_dates, date_range))

    return date_range[mask]
