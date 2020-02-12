#!/usr/bin/env python

import copy
import sys
import pandas as pd
import numpy as np

from ..src_webapp.constants import (
    CONST_COL_NAME_DATE,
    CONST_COL_NAME_COST,
    CONST_COL_NAME_YM,
    CONST_COL_NAME_IDEALCOST,
    CONST_COL_NAME_AVAILCOST,
    CONST_COL_NAME_SUB,
    CONST_COL_NAME_SGUID
)

from ..src_webapp.data_loader import create_dataframe

from ..src_webapp.utilities import diff_month
from ..src_webapp.totals import group_year_month, add_missing_year_months
from ..src_webapp.subs import get_data_for_subid

# from src_webapp.constants import (
#     CONST_COL_NAME_DATE,
#     CONST_COL_NAME_COST,
#     CONST_COL_NAME_YM,
#     CONST_COL_NAME_IDEALCOST,
#     CONST_COL_NAME_AVAILCOST,
#     CONST_COL_NAME_SUB,
#     CONST_COL_NAME_SGUID
# )

# from src_webapp.data_loader import create_dataframe

# from src_webapp.utilities import diff_month
# from src_webapp.totals import group_year_month, add_missing_year_months
# from src_webapp.subs import get_data_for_subid

from dateutil.relativedelta import relativedelta

class EA_budget:
    def __init__(self, name, dt_from, dt_to, amount, currency):
        self.name = name
        self.dt_from = dt_from
        self.dt_to = dt_to
        self.amount = amount
        self.currency = currency

def create_cost_avail_ideal_df(ea_budget, ea_usage, date_from, date_to, max_reg_cost_day,
    use_days=False):
    """
        Creates a dataframe with actual, ideal and available costs for an EA budget

        Args:
            ea_budget - EA budget
            ea_usage - EA usage dataframe
            date_from - analysis period start date (e.g. financial year start)
            date_to - analysis period end date (e.g. financial year end)
            mmax_reg_cost_day - the present (max date with sponsorship usage)
            use_days - a flag to use days for estimation, otherwise months
        Returns:
            ea_df - a dataframe actual, ideal and available costs for an EA budget
    """

    if ea_usage is not None:
        # TODO: budget_spent needs to be estimated depending on the date
        sys.exit(1)
    else:
        budget_spent = 0.0

    # EA budget has expired or has not started yet
    if ea_budget.dt_to < date_from or ea_budget.dt_from > date_to:
        return None

    budget_days = (ea_budget.dt_to - ea_budget.dt_from).days
    budget_months = diff_month(ea_budget.dt_to, ea_budget.dt_from)

    budget_avg_day = float(ea_budget.amount) / float(budget_days)
    budget_avg_month = float(ea_budget.amount) / float(budget_months)

    budget_left = ea_budget.amount - budget_spent

    budget_days_left = max((ea_budget.dt_to - max_reg_cost_day).days, 0)
    budget_months_left = max(diff_month(ea_budget.dt_to, copy.copy(max_reg_cost_day).replace(day=1) - relativedelta(days=1)), 0)

    budget_left_avg_day = float(budget_left) / float(budget_days_left)
    budget_left_avg_month = float(budget_left) / float(budget_months_left)

    cur_date = copy.copy(date_from).replace(day=1)

    year_month_list = []
    ideal_list = []
    avail_list = []

    while cur_date <= date_to:

        month_st = max(copy.copy(cur_date).replace(day=1), date_from)
        month_end = min(copy.copy(cur_date).replace(day=1) + relativedelta(months=1) - relativedelta(days=1), date_to)

        days_cnt = (month_end - month_st).days
        year_month = '{year}-{month:02d}'.format(year=month_st.year, month=month_st.month)

        # Check if the month has passed
        full_month = (max_reg_cost_day >= month_end)

        if full_month:
            if ea_budget.dt_from >= month_end:
                monthly = 0.0
            else:
                if use_days:
                    monthly = budget_avg_day * days_cnt
                else:
                    monthly = budget_avg_month

            monthly_avail = None
        else:
            monthly = None

            if month_end <= ea_budget.dt_to:
                if use_days:
                    monthly_avail = budget_left_avg_day * days_cnt
                else:
                    monthly_avail = budget_left_avg_month
            else:
               monthly_avail = 0.0

        year_month_list.append(year_month)
        ideal_list.append(monthly)
        avail_list.append(monthly_avail)

        cur_date += relativedelta(months=1)

    d = {CONST_COL_NAME_YM: year_month_list,
         CONST_COL_NAME_IDEALCOST: ideal_list, CONST_COL_NAME_AVAILCOST: avail_list}

    df = pd.DataFrame(data=d)

    return df

def analyse_ea_usage(budgets, ea_data_df, date_from, date_to, max_reg_cost_day):
    """

        Args:
            budgets - a list of EA_budget budegts containing all the available EA budgets
            ea_data_df - a dataframe with all the EA usage data
            date_from - analysis period start date (e.g. financial year start)
            date_to - analysis period end date (e.g. financial year end)
            max_reg_cost_day - the present (max date with sponsorship usage)
        Returns:
            ea_budget
            ea_usage
            ea_remain
            main_budget_df
    """

    if ea_data_df is not None:
        sys.exit(1)
    else:
        print("WARNING : ATM analysis does not include EA usage data")
        print("WARNING : ATM analysis does not include EA usage data")
        print("WARNING : ATM analysis does not include EA usage data")

    main_budget_df = None
    for ea_budget in budgets:
        budget_df = create_cost_avail_ideal_df(ea_budget, ea_data_df, date_from, date_to, max_reg_cost_day)

        if main_budget_df is None:
            main_budget_df = copy.deepcopy(budget_df)
        else:
            main_budget_df[CONST_COL_NAME_IDEALCOST] = main_budget_df[CONST_COL_NAME_IDEALCOST] + budget_df[CONST_COL_NAME_IDEALCOST]
            main_budget_df[CONST_COL_NAME_AVAILCOST] = main_budget_df[CONST_COL_NAME_AVAILCOST] + budget_df[CONST_COL_NAME_AVAILCOST]

    if ea_data_df is None:
        main_budget_df[CONST_COL_NAME_COST] = 0.0
        ea_budget = main_budget_df[CONST_COL_NAME_AVAILCOST].sum()

    else:
        sys.exit(1)
        ea_budget = None

    ea_usage = main_budget_df[CONST_COL_NAME_COST].sum()
    ea_remain = ea_budget - ea_usage

    return ea_budget, ea_usage, ea_remain, main_budget_df

def analyse_spnsr_usage(data_path, date_from, date_to, spnsr_budget):
    """
    Performs analysis for usage of sponsorship budegt

    Args:
        spnsr_data_path - path to the directory which contains all available usage data from both
            the sponsorship portal and EduHub
        date_from - analysis period start date (e.g. financial year start)
        date_to - analysis period end date (e.g. financial year end)
        spnsr_budget - sponsorship budget for the analysis period (e.g. financial year)

    Returns:
        spnsr_remain - total remnain budget for the specified period
        spnsr_usage - total usage over the specified period
        spnsr_usage_df - data frame with usage analysis
        max_reg_cost_day - the present (max date with sponsorship usage)

    """

    # reading in the data
    data_df = create_dataframe(data_path)

    # applying data filters
    sub_data_df = data_df[(data_df.Date >= date_from) & (data_df.Date <= date_to)]

    spnsr_usage = sub_data_df[CONST_COL_NAME_COST].sum()
    spnsr_remain = spnsr_budget - spnsr_usage

    spnsr_usage_ym_df = group_year_month(sub_data_df)

    # adding zeros for the missing year-months
    spnsr_usage_ym_df = add_missing_year_months(spnsr_usage_ym_df,
        date_from, date_to, CONST_COL_NAME_COST)

    # estimates ideal and available costs
    spnsr_ideal_avail_ym_df, max_reg_cost_day = get_ideal_avail_spnsr_costs(sub_data_df,
        date_from, date_to, spnsr_budget)

    # reset index
    spnsr_usage_ym_df = spnsr_usage_ym_df.reset_index(drop=True)
    spnsr_ideal_avail_ym_df = spnsr_ideal_avail_ym_df.reset_index(drop=True)

    # combining actual, ideal and available costs into one dataframe
    spnsr_usage_df = pd.concat([spnsr_ideal_avail_ym_df,
        spnsr_usage_ym_df.drop([CONST_COL_NAME_YM], axis=1)], axis=1)

    return spnsr_remain, spnsr_usage, spnsr_usage_df, max_reg_cost_day

def get_ideal_avail_spnsr_costs(sub_raw_data_df, spnsr_date_from, spnsr_date_to,
    spnsr_budget, use_days = False):
    """ Estimates the ideal spending scenario and available costs based on the usage during
        the analysis period.

    Args:
        sub_raw_data_df - raw usage dataframe
        date_from - analysis period start date (eg. financial year start)
        date_to - analysis period end date (eg. financial year end)
        spnsr_budget - sponsorship budget for the analysis period (e.g. financial year)
        use_days - a flag to use days for estimation, otherwise months
    Returns:
        df - a dataframe with an ideal spending scenario and available budget
        max_reg_cost_day - the present (max date with sponsorship usage)

    """

    date_from = spnsr_date_from
    date_to = spnsr_date_to + relativedelta(days=1)

    # registering the latest date with registered usage
    max_reg_cost_day = pd.to_datetime(max(sub_raw_data_df[CONST_COL_NAME_DATE]))

    budget_spent = sub_raw_data_df[CONST_COL_NAME_COST].sum()
    budget_left = spnsr_budget - budget_spent

    # number of days/months within the analysis period
    days_total = (date_to - date_from).days

    months_total = diff_month(date_to, date_from)

    if days_total <= 0:
        return pd.DataFrame()

    # average dayly/monthly allocated budget during the analysis period
    day_avg_budget = float(spnsr_budget) / float(days_total)
    month_avg_budget = float(spnsr_budget) / float(months_total)

    # number of days/months left (no usage registered yet) during the analysis period
    days_left = max((date_to - max_reg_cost_day).days, 0)
    months_left = max(diff_month(date_to, max_reg_cost_day), 0)

    # average dayly/monthly left available for the analysis period
    day_left_avg_budget = float(budget_left) / float(days_left)
    month_left_avg_budget = float(budget_left) / float(months_left)

    # Iterates through the months of the analysis period and estinates ideal and available costs.
    # Ideal costs is the spnsr_budget equally distributed over the months of the analysis period.
    # Available costs are unspent budget distributed equally over the future months (months withough registered usage)

    year_month_list = []
    ideal_cost_list = []
    avail_cost_list = []

    cur_date = date_from

    while cur_date < date_to:

        month_st = max(copy.copy(cur_date).replace(day=1), date_from)
        month_end = min(copy.copy(cur_date).replace(day=1) + relativedelta(months=1) - relativedelta(days=1), date_to)

        days_cnt = (month_end - month_st).days
        year_month = '{year}-{month:02d}'.format(year=month_st.year, month=month_st.month)

        # Check if the month has passed
        full_month = (max_reg_cost_day >= month_end)

        if full_month:
            if use_days:
                ideal_cost = days_cnt * day_avg_budget
            else:
                ideal_cost = month_avg_budget

            avail_cost = None
        else:
            if use_days:
                avail_cost = days_cnt * day_left_avg_budget
            else:
                avail_cost = month_left_avg_budget

            ideal_cost = None

        year_month_list.append(year_month)
        ideal_cost_list.append(ideal_cost)
        avail_cost_list.append(avail_cost)

        cur_date += relativedelta(months=1)

    d = {CONST_COL_NAME_YM: year_month_list,
        CONST_COL_NAME_IDEALCOST: ideal_cost_list,
        CONST_COL_NAME_AVAILCOST: avail_cost_list}

    df = pd.DataFrame(data=d)

    return df, max_reg_cost_day

def get_detailed_spnsr_analysis_df(data_path, date_from, date_to):

    # reading in the data
    data_df = create_dataframe(data_path)

    # applying data filters
    df = data_df[(data_df.Date >= date_from) & (data_df.Date <= date_to)]

    # Getting DSG's data
    dsg_ids = get_DSGs_IDs()

    dsg_name = "Data Study Groups"
    dsg_guid = '1'
    dsg_df = agg_totals_sub_group(df, dsg_ids, dsg_name, dsg_guid)

    # raw data excluding dsgs
    sub_raw_data_df_no_dsgs = get_data_excl_subid(df, dsg_ids)

    total_from = 0.0
    total_to = 1000.0
    sub_id_2 = '2'

    sub_ids_0_1, sub_grp_totals_0_1_df = agg_subs_with_total_usage(sub_raw_data_df_no_dsgs,
                                                                           total_from, total_to,
                                                                           sub_id_2, "NA")
    sub_name_2 = "{} Subscriptions with {:d} to {:d} spent".format(len(sub_ids_0_1), int(total_from), int(total_to))

    total_from = 1000.0
    total_to = 5000.0
    sub_id_3 = '3'
    sub_ids_1_5, sub_grp_totals_1_5_df = agg_subs_with_total_usage(sub_raw_data_df_no_dsgs,
                                                                           total_from, total_to,
                                                                           sub_id_3, "NA")
    sub_name_3 = "{} Subscriptions with {:d} to {:d} spent".format(len(sub_ids_1_5), int(total_from), int(total_to))

    total_from = 5000.0
    total_to = 10000.0
    sub_id_4 = '4'
    sub_ids_5_10, sub_grp_totals_5_10_df = agg_subs_with_total_usage(sub_raw_data_df_no_dsgs,
                                                                           total_from, total_to,
                                                                           sub_id_4, "NA")
    sub_name_4 = "{} Subscriptions with {:d} to {:d} spent".format(len(sub_ids_5_10), int(total_from), int(total_to))

    exclude_list = dsg_ids + sub_ids_0_1 + sub_ids_1_5 + sub_ids_5_10

    excl_df = group_sub_year_month(get_data_excl_subid(df, exclude_list))

    excl_df.insert(0, CONST_COL_NAME_SUB, '')
    excl_df[CONST_COL_NAME_SUB] = excl_df[CONST_COL_NAME_SGUID].apply(lambda x: get_sub_latest_name(df, x))

    final_df = pd.concat([excl_df, dsg_df,
                          sub_grp_totals_0_1_df,
                          sub_grp_totals_1_5_df,
                          sub_grp_totals_5_10_df], sort=False)

    final_pivot = pd.pivot_table(final_df, index=CONST_COL_NAME_SGUID,
                                        columns=CONST_COL_NAME_YM,
                                        values=CONST_COL_NAME_COST,
                                        aggfunc=np.sum, margins=True)

    masked_pivot = final_pivot.replace(np.nan, '', regex=True)

    result = masked_pivot.sort_values(('All'), ascending=False)

    pivot_df = pd.DataFrame(result.to_records())

    pivot_df.insert(0, CONST_COL_NAME_SUB, '')
    pivot_df[CONST_COL_NAME_SUB] = pivot_df[CONST_COL_NAME_SGUID].apply(lambda x: get_sub_latest_name(df, x))


    # Updating Subscription names and ids
    pivot_df.loc[pivot_df.SubscriptionGuid == dsg_guid, CONST_COL_NAME_SUB] = dsg_name
    pivot_df.loc[pivot_df.SubscriptionGuid == sub_id_2, CONST_COL_NAME_SUB] = sub_name_2
    pivot_df.loc[pivot_df.SubscriptionGuid == sub_id_3, CONST_COL_NAME_SUB] = sub_name_3
    pivot_df.loc[pivot_df.SubscriptionGuid == sub_id_4, CONST_COL_NAME_SUB] = sub_name_4
    pivot_df.loc[pivot_df.SubscriptionGuid == "All", CONST_COL_NAME_SUB] = "Total"

    return pivot_df

###### NO UNIT TESTS FOR ALL THE FOLLWING FUNCTIONS

def get_data_excl_subid(raw_data, sub_ids):
    """Filters data excluding particular subscription id or a list of subscription ids
    Args:
        raw_data: raw usage dataframe
        sub_ids: subscription id or a list of subscription ids
    """

    if isinstance(sub_ids, (list,)):
        return raw_data[~raw_data.SubscriptionGuid.isin(sub_ids)]
    else:
        return raw_data[raw_data.SubscriptionGuid != sub_ids]

def agg_totals_sub_group(df, sub_ids, sub_name, sub_id):
    """ Aggregates the costs for a group of subscriptions based on their ids
    Args:
        df - raw usage data
        sub_ids - a list of subscription ids
        sub_name - a name of subscriptions group
        sub_id - fictitious subscription id
    Returns:
        sub_group_df - a resulting dataframe
    """

    sub_group_df = group_year_month(get_data_for_subid(df, sub_ids))
    sub_group_df[CONST_COL_NAME_SGUID] = sub_id
    sub_group_df[CONST_COL_NAME_SUB] = sub_name

    return sub_group_df

def get_DSGs_IDs():
    print("WARNING: ", "get_DSGs_IDs: ", "Are DSG IDs up to day?")

    dsg_ids = ['{3304DEF8-15AF-4DA2-8D4C-50A3BD9F5114}',
                '{EB9F30AA-04C9-4779-8B8A-2D08285142F2}',
                '{F484347F-982E-4553-8978-213F8AF3FD43}',
                '{47D02213-61A2-4113-9126-322C8876BE2F}',
                '{362F5084-5218-4B19-85C1-F7FF9E872046}',
                '{71E21E4C-4177-4CF1-AB25-6A88E52EDD03}',
                '{FB631FDE-18F2-45F4-B018-D622DC16D94E}',
                '{7D83CCB2-E88A-43B8-AF34-7E1D74BE3C40}',
                '{F2F151B9-2AF6-4E1D-9CD4-FB80E59D3BDF}',
                '{9259CB1C-EAA3-4301-889E-F8C9988A4AD3}',
                '{93077F61-2D19-480C-9994-4FAFDD6185D2}',
                '{2CD64292-4240-4274-98ED-FC86AB395280}',
                '{D2B3BB29-ADD7-44A1-8185-93C6155C7169}',
                '{4E8AC81B-220D-4B93-88E4-75F27A5D8AD1}',
                '{90B42CAC-AE2D-45C1-A8B1-B26839FF20F1}',
                '{0503155C-2BFE-4CDE-89EC-038EA288E79D}',
                '{E305A285-A056-4173-91DA-F7623E0A4524}',
                '{9C3DC1EE-CF80-4C32-95AB-8F32B0CEA40C}',
                '{813E99A0-5C7C-4C43-AFD3-2A9566880854}',
                '{BE6D41C8-4D43-4890-AF25-771D40272758}',
                '{AFE7C62F-CF25-44B3-9E56-D7A14A3EA5E4}',
                '{F871C3F7-6A68-42FB-BED6-81689E730F7A}',
                '{1BA6669A-274F-407C-96D7-53BE98300C5F}',
                '{95ACC417-CC03-47A5-8356-5746187DD1F8}',
                '{0045F23F-5F08-46DD-ACD3-4900DF4324B3}',
                '{A88DB981-D063-486A-BC2D-58DC20455F32}',
                '{0F84BE1D-CEE9-439A-9218-DCEB1AE2BF21}',
                '{73206399-6F5A-44CC-B190-77C1A238D36B}',
                '{86AAF003-3C41-43F5-BA0E-C834C3949E80}',
                '{F23BAA60-1BD7-4B16-B9AD-AD905ADD9F74}',
                '{D45183A8-1476-4097-BBA5-6E50AC38D1CF}',
                '{C5DF9808-1109-4804-8F5F-EC54D6D2A10F}',
                '{34C1DA4E-C612-4FA3-A9A7-FDF5B1BC4BB0}',
                '{91A3CCC7-1E9F-4944-A3B6-4A5800EF5341}',
                '{3D36AD79-2C59-4A9B-B281-33707540168E}',
                '{712EF6E4-1373-4462-A239-9716D3F207DB}',
                '{2CFBEFAC-5C00-4B90-8512-311A7430F548}',
                '{C90191BD-4ECD-4C9B-9283-23A61DC822D5}',
                '{9DB57597-498F-4A44-8580-7BB5F31CBA94}',
                '{1F82E26B-36E9-4B24-8F8A-3CADF98257C8}',
                '{4312ADF2-DBE4-4090-A424-3FB6BE97EF49}',
                '{37471D1B-2D3F-42F9-A93C-517BDC0CAB18}',
                '{FC3971E4-3998-496D-B446-BEA651FB398B}',
                ]

    return dsg_ids

def agg_subs_with_total_usage(df, total_from, total_to, sub_id, sub_name):
    """ Aggregates the costs for subscriptions with total costs within a set range
    Args:
        df - raw usage data
        total_from -
        total_to -
        sub_id - a fictitious subscription id
        sub_name - a name of subscriptions group
    Returns:
        sub_ids - a list of subscription IDs with total costs within a set range
        res_df - a resulting dataframe
    """

    df_gr = df.groupby([CONST_COL_NAME_SGUID])[CONST_COL_NAME_COST].sum().reset_index()

    df_gr_wh = df_gr[(df_gr.Cost >= total_from) & (df_gr.Cost < total_to)]

    sub_ids = list(df_gr_wh[CONST_COL_NAME_SGUID].values)

    res_df = agg_totals_sub_group(df, sub_ids, sub_name, sub_id)

    return sub_ids, res_df

def group_sub_year_month(raw_data):
    """Groups raw usage by calender month and subscriptionid
    Args:
        raw_data: raw usage data framework
    Returns:
        raw_data_gr: dataframe of grouped raw usage by calender month
    """

    raw_data_ = raw_data.copy()
    raw_data_[CONST_COL_NAME_YM] = pd.to_datetime(raw_data_[CONST_COL_NAME_DATE]).apply(lambda x: '{year}-{month:02d}'.format(year=x.year, month=x.month))

    raw_data_gr = raw_data_.groupby([CONST_COL_NAME_SGUID, CONST_COL_NAME_YM])[CONST_COL_NAME_COST].sum().reset_index().sort_values(by=[CONST_COL_NAME_YM], ascending=True)

    return raw_data_gr

def get_sub_latest_name(raw_data_df, sub_id):
    """Returns the latest subscription name from the raw data for a particular subscription id
    Args:
        raw_data_df: raw usage data framework
        sub_id: subscription id
    Returns:
        subscription name
    """

    raw_data_df_temp = raw_data_df[raw_data_df.SubscriptionGuid == sub_id]

    raw_sub_last_df = raw_data_df_temp[["SubscriptionGuid", "Date", "SubscriptionName"]].groupby(['SubscriptionGuid']).agg('max').reset_index()

    try:
        return str(raw_sub_last_df["SubscriptionName"][0])
    except:
        return "NA"