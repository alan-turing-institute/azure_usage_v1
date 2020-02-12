#!/usr/bin/python
"""
Python module to perform operations related to subscriptions

Author: Tomas Lazauskas
"""

import pandas as pd
import copy
from math import pi

from .constants import (
    CONST_COL_NAME_SGUID,
    CONST_COL_NAME_DATE,
    CONST_COL_NAME_COST,
    CONST_COL_NAME_SERVICETYPE,
    CONST_COL_NAME_SERVICE,
    CONST_COL_NAME_SERVICENAME,
    CONST_COL_NAME_SERVICERESOURCE,
    CONST_COL_NAME_SUM,
    CONST_NAME_OTHER,
    CONST_COL_NAME_PERC,
    CONST_COL_NAME_ANGLE,
    CONST_NONE,
    CONST_MAX_TOP_SERVICES,
    CONST_MAX_SERVICE_LENGTH,
    CONST_RB_DEFAULT,
    CONST_RB_VALUE_1,
    CONST_RB_VALUE_2,
    CONST_RB_VALUE_3
)

from bokeh.palettes import Category20c

def get_data_for_subid(raw_data, sub_ids):
    """Filters data for a particular subscription id or a list of subscription ids
    Args:
        raw_data: raw usage dataframe
        sub_ids: subscription id or a list of subscription ids
    """

    if isinstance(sub_ids, (list,)):
        return raw_data[raw_data.SubscriptionGuid.isin(sub_ids)]
    else:
        return raw_data[raw_data.SubscriptionGuid == sub_ids]

def get_top_services(raw_data_df, top_services_num=None, top_services_grp_md=CONST_RB_DEFAULT):
    """ Prepares top services dataframe
    Args:
        raw_data_df: raw usage dataframe for a subscription
    Returns:
        datframe with top services
    """

    # checking if raw_data_df is a pandas dataframe
    if not isinstance(raw_data_df, pd.DataFrame):
        return None

    # checking if raw_data_df is empty and has no columns
    if raw_data_df.empty and len(raw_data_df.columns) == 0:
        return None
    
    if top_services_num is None:
        top_services_cnt = CONST_MAX_TOP_SERVICES
    else:
        top_services_cnt = top_services_num

    grp_srv = copy.copy(raw_data_df)
    
    # creating new column to hold information about service
    if top_services_grp_md == CONST_RB_VALUE_1:
        grp_srv[CONST_COL_NAME_SERVICE] = (grp_srv[CONST_COL_NAME_SERVICENAME] + ": " + grp_srv[CONST_COL_NAME_SERVICETYPE] + ": " + grp_srv[CONST_COL_NAME_SERVICERESOURCE])
    elif top_services_grp_md == CONST_RB_VALUE_2:
        grp_srv[CONST_COL_NAME_SERVICE] = (grp_srv[CONST_COL_NAME_SERVICENAME] + ": " + grp_srv[CONST_COL_NAME_SERVICETYPE])
    elif top_services_grp_md == CONST_RB_VALUE_3:
        grp_srv[CONST_COL_NAME_SERVICE] = (grp_srv[CONST_COL_NAME_SERVICENAME] + ": " + grp_srv[CONST_COL_NAME_SERVICERESOURCE])
    else:
        grp_srv[CONST_COL_NAME_SERVICE] = grp_srv[CONST_COL_NAME_SERVICETYPE]
    
    # grouping the data
    grp_srv = grp_srv.groupby([CONST_COL_NAME_SERVICE])[CONST_COL_NAME_COST].agg(CONST_COL_NAME_SUM).reset_index()
    
    # truncating service column's values
    grp_srv[CONST_COL_NAME_SERVICE] = grp_srv[CONST_COL_NAME_SERVICE].str[:CONST_MAX_SERVICE_LENGTH]
    
    # sorting and reseting index
    grp_srv = grp_srv.sort_values(CONST_COL_NAME_COST, ascending=False)
    grp_srv.reset_index(inplace=True, drop=True)
    
    # Creating a dataframe with the line Other, i.e. <= min_cost
    if len(grp_srv.index) > top_services_cnt:
        
        top_srv = grp_srv.iloc[:top_services_cnt]
        
        other_temp_df = grp_srv.iloc[top_services_cnt:]
        other_sum = other_temp_df[CONST_COL_NAME_COST].agg(CONST_COL_NAME_SUM)
        other_df = pd.DataFrame([[CONST_NAME_OTHER + " (%d)" % (len(other_temp_df)), other_sum]], columns=[CONST_COL_NAME_SERVICE, CONST_COL_NAME_COST])

    else:
        top_srv = copy.copy(grp_srv)
        other_sum = 0

    # Combining the data frames
    if other_sum > 0:
        top_srv = top_srv.append(other_df)
        top_srv = top_srv.sort_values(CONST_COL_NAME_COST, ascending=False)

    # Adding percentage column
    top_sum = top_srv[CONST_COL_NAME_COST].sum()

    top_srv = top_srv.copy()

    if top_sum > 0:
        top_srv[CONST_COL_NAME_PERC] = top_srv[CONST_COL_NAME_COST]/top_sum
    else:
        top_srv[CONST_COL_NAME_PERC] = 100

    return top_srv

def calc_top_services_perc(global_sub_service_grp):
    '''Estimates percentages for top services

    Args:
        global_sub_service_grp - a grouped top services data frame

    Returns an updated global_sub_service_grp object
    '''

    # not global_sub_raw_usage.empty and 
    if not global_sub_service_grp.empty:
        global_sub_service_grp[CONST_COL_NAME_ANGLE] = global_sub_service_grp[CONST_COL_NAME_COST]/global_sub_service_grp[CONST_COL_NAME_COST].sum() * 2*pi
        global_sub_service_grp['color'] = Category20c[len(global_sub_service_grp)]

    else:
        global_sub_service_grp[CONST_COL_NAME_ANGLE] = 0
        global_sub_service_grp['color'] = ""

    return global_sub_service_grp