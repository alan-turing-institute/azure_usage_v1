"""
A script to prepare a single Azure raw usage file by combining
    multiple files and removing duplicates.
"""

import argparse
import sys
import os
from pandas import Timestamp

from src_webapp.data_loader import create_dataframe
from src_webapp.constants import TIMESTAMP_FILE

sys.path.append("./azure_usage/")

__COMBINED_USAGE = ""


def setup():
    """
    Prepared arguments for the command line
    """

    parser = argparse.ArgumentParser(
        description="Prepare raw Azure usage data."
    )
    parser.add_argument(
        "-i", "--input", help="Path to the input files", required=True
    )
    parser.add_argument(
        "-o", "--output", help="Path to the output directory", required=True
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    args = setup()

    # Checking paths
    if not os.path.isdir(args.input):
        raise Exception(args.input + " cannot be accessed.")

    if not os.path.isdir(args.output):
        raise Exception(args.output + " cannot be accessed.")

    raw_usage = create_dataframe(args.input)

    dt_st = raw_usage["Date"].min()
    dt_end = raw_usage["Date"].max()

    output_file_name = "{year_end}-{month_end:02d}-{day_end:02d}".format(
        year_end=dt_end.year, month_end=dt_end.month, day_end=dt_end.day
    )
    output_file_name = "{}-{year_st}-{month_st:02d}-{day_st:02d}.csv".format(
        output_file_name,
        year_st=dt_st.year,
        month_st=dt_st.month,
        day_st=dt_st.day,
    )

    raw_usage.to_csv(os.path.join(args.output, output_file_name))

    # creating a time stamp when data was prepared
    timestamp_f = open(os.path.join(args.output, TIMESTAMP_FILE), "w")
    timestamp_f.write("{}\n".format(Timestamp.now()))
    timestamp_f.close()
