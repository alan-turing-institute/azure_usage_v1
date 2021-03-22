"""
test Bokeh server

Author: Tomas Lazauskas
"""

import os
import pandas as pd

from ..src_webapp.bokeh_server import (
    readin_data,
    create_updates_tab,
    create_about_tab,
    create_usage_bar_plot,
    create_top_services_pie_plot,
    # initiliase_data_sources,
)

from bokeh.models.widgets import Panel
from bokeh.plotting import Figure

from ..src_webapp.constants import (
    CONST_TEST_DIR_DATA_LOADER,
    # CONST_TEST_DIR_1,
    CONST_TEST_DIR_3,
)


def test_readin_data():
    """
    Testing simple import from a test directory with multiple files

    """
    global global_raw_usage

    data_path = os.path.join(CONST_TEST_DIR_DATA_LOADER, CONST_TEST_DIR_3)

    # reads in the raw usage data
    global_raw_usage, last_update = readin_data(data_path)

    # counting the number of entries
    assert len(global_raw_usage.index) == 3
    assert last_update == pd.to_datetime("2019-12-12 15:49:30.988079")


def test_create_updates_tab():
    assert isinstance(create_updates_tab(), (Panel,))


def test_create_about_tab():
    assert isinstance(create_about_tab(), (Panel,))


def test_create_usage_bar_plot():
    assert isinstance(create_usage_bar_plot(), (Figure,))


def test_create_top_services_pie_plot():
    assert isinstance(create_top_services_pie_plot(), (Figure,))
