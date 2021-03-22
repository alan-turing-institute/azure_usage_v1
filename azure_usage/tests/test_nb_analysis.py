"""
Test analysis functions for the notebook

Author: Tomas Lazauskas
"""

import os
import pandas as pd
from ..src_webapp.data_loader import create_dataframe

from ..src_notebook.analysis import (
    get_ideal_avail_spnsr_costs,
    analyse_spnsr_usage,
    analyse_ea_usage,
    EA_budget,
    create_cost_avail_ideal_df,
    get_detailed_spnsr_analysis_df,
)

from ..src_webapp.constants import (
    CONST_TEST_DIR_DATA_LOADER,
    CONST_TEST_DIR_8,
    CONST_COL_NAME_AVAILCOST,
    CONST_COL_NAME_IDEALCOST,
    CONST_COL_NAME_COST,
)


def test_get_ideal_avail_spnsr_costs():

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_8)

    raw_usage = create_dataframe(data_path)

    date_from = pd.to_datetime("2019-10-01")
    date_to = pd.to_datetime("2020-09-30")
    spnsr_budget = 1000000

    result_df, max_reg_cost_day = get_ideal_avail_spnsr_costs(
        raw_usage, date_from, date_to, spnsr_budget, use_days=False
    )

    assert max_reg_cost_day == pd.to_datetime("2019-11-11")

    print(result_df)

    # test avail cost
    avail_cost = round(spnsr_budget - raw_usage[CONST_COL_NAME_COST].sum(), 9)
    avail_cost_sum = round(result_df[CONST_COL_NAME_AVAILCOST].sum(), 9)

    assert avail_cost_sum == avail_cost

    ideal_cost_sum = round(result_df[CONST_COL_NAME_IDEALCOST].sum(), 9)

    assert ideal_cost_sum == 83333.333333333


def test_analyse_spnsr_usage():

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_8)
    date_from = pd.to_datetime("2019-10-01")
    date_to = pd.to_datetime("2020-09-30")
    spnsr_budget = 1000000

    (
        spnsr_remain,
        spnsr_usage,
        spnsr_usage_df,
        max_reg_cost_day,
    ) = analyse_spnsr_usage(data_path, date_from, date_to, spnsr_budget)

    assert max_reg_cost_day == pd.to_datetime("2019-11-11")

    spnsr_usage = round(spnsr_usage, 9)
    total_cost = round(spnsr_usage_df[CONST_COL_NAME_COST].sum(), 9)
    assert spnsr_usage == total_cost

    spnsr_remain = round(spnsr_remain, 9)
    remain = round(spnsr_budget - spnsr_usage, 9)
    assert spnsr_remain == remain

    total_avail = round(spnsr_usage_df[CONST_COL_NAME_IDEALCOST].sum(), 9)
    assert total_avail == 83333.333333333


def test_create_cost_avail_ideal_df():

    # TEST CASE 1
    budget = EA_budget(
        "ASG (aka SPFA)",
        pd.to_datetime("2019-01-01"),
        pd.to_datetime("2020-03-31"),
        321897.25,
        "USD",
    )

    dt_from = pd.to_datetime("2019-10-01")
    dt_to = pd.to_datetime("2020-09-30")

    dt_now = pd.to_datetime("2019-11-06")

    ea_usage = None
    ea_df = create_cost_avail_ideal_df(
        budget, ea_usage, dt_from, dt_to, dt_now
    )

    total_ideal = round(ea_df[CONST_COL_NAME_IDEALCOST].sum(), 9)
    ideal_calc = round(budget.amount / 14.0, 9)
    assert ideal_calc == total_ideal

    total_avail = round(ea_df[CONST_COL_NAME_AVAILCOST].sum(), 9)
    assert budget.amount == total_avail

    # TEST CASE 2
    budget = EA_budget(
        "LwM",
        pd.to_datetime("2019-04-01"),
        pd.to_datetime("2024-03-31"),
        321897.25,
        "USD",
    )

    dt_from = pd.to_datetime("2019-10-01")
    dt_to = pd.to_datetime("2020-09-30")

    dt_now = pd.to_datetime("2019-11-06")

    ea_usage = None
    ea_df = create_cost_avail_ideal_df(
        budget, ea_usage, dt_from, dt_to, dt_now
    )

    total_ideal = round(ea_df[CONST_COL_NAME_IDEALCOST].sum(), 9)
    ideal_calc = round(budget.amount / 59.0, 9)
    assert ideal_calc == total_ideal

    total_avail = round(ea_df[CONST_COL_NAME_AVAILCOST].sum(), 9)
    assert 66808.863207547 == total_avail


def test_analyse_ea_usage():

    budgets = []

    # ASG aka SPFA
    budgets.append(
        EA_budget(
            "ASG (aka SPFA)",
            pd.to_datetime("2019-01-01"),
            pd.to_datetime("2020-03-31"),
            250000,
            "GBP",
        )
    )

    # LWM
    budgets.append(
        EA_budget(
            "LwM",
            pd.to_datetime("2019-04-01"),
            pd.to_datetime("2024-03-31"),
            250000,
            "GBP",
        )
    )

    ea_data_df = None

    dt_from = pd.to_datetime("2019-10-01")
    dt_to = pd.to_datetime("2020-09-30")

    dt_now = pd.to_datetime("2019-11-06")

    ea_budget, ea_usage, ea_remain, ea_df = analyse_ea_usage(
        budgets, ea_data_df, dt_from, dt_to, dt_now
    )
    print(ea_df)
    assert ea_budget == 301886.79245283024

    total_ideal = round(ea_df[CONST_COL_NAME_IDEALCOST].sum(), 9)
    assert 22094.430992736 == total_ideal

    total_avail = round(ea_df[CONST_COL_NAME_AVAILCOST].sum(), 9)
    assert 301886.79245283 == total_avail


def test_get_detailed_spnsr_analysis_df():

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_8)

    date_from = pd.to_datetime("2019-10-01")
    date_to = pd.to_datetime("2020-09-30")

    # smoke test run
    _ = get_detailed_spnsr_analysis_df(data_path, date_from, date_to)

    assert True
