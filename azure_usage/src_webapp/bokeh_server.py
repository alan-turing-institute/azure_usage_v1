"""
Main bokeh server module
"""

import os
from math import pi
import pandas as pd

# Bokeh imports
from bokeh.plotting import figure
from bokeh.layouts import row, column, layout
from bokeh.models import (
    ColumnDataSource,
    DatetimeTickFormatter,
)
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from bokeh.models.widgets import (
    TextInput,
    DataTable,
    TableColumn,
    NumberFormatter,
    Div,
    DatePicker,
    Tabs,
    Panel,
    PreText,
    RadioButtonGroup,
)

# azure_usage imports
from .constants import (
    CONST_COL_NAME_COST,
    CONST_COL_NAME_SERVICE,
    CONST_COL_NAME_ANGLE,
    CONST_COL_NAME_PERC,
    CONST_COL_NAME_DATE,
    DATA_FOLDER,
    README_FILE,
    UPDATES_FILE,
    URL_PARAM_REPORT,
    URL_PARAM_SUB_IDS,
    URL_PARAM_DT_FROM,
    URL_PARAM_DT_TO,
    CONST_RB_DEFAULT,
    CONST_RB_LABEL_0,
    CONST_RB_LABEL_1,
    CONST_RB_LABEL_2,
    CONST_RB_LABEL_3,
    CONST_ENCODING,
    DEFAULT_REPORT_NAME,
    TIMESTAMP_FILE,
)

from .subs import get_data_for_subid, get_top_services, calc_top_services_perc

from .totals import group_day
from .utilities import prep_sub_ids, parse_url_params, read_timestamp
from .data_loader import create_dataframe


# Global variables
GLOBAL_RAW_USAGE = None
GLOBAL_LAST_UPDATE = None
GLOBAL_SUB_RAW_USAGE = None
GLOBAL_SUB_SERVICE_GRP = None

GLOBAL_TOTAL_SOURCE = None

GLOBAL_WIDGET_SUBID = TextInput()
GLOBAL_DATE_PICKER_FROM = None
GLOBAL_DATE_PICKER_TO = None
GLOBAL_WIDGET_SUBSCRIPTION_NAMES = None
GLOBAL_WIDGET_TOTAL_TEXT = None
GLOBAL_WIDGET_TOP_SERVICES_RB = None

GLOBAL_S1 = None
GLOBAL_S2 = None

GLOBAL_TOP_SERVICE_SOURCE = None

GLOBAL_PWD = os.path.dirname(os.path.realpath(__file__))


def readin_data(data_path=None):
    """ Reads in raw Azure usage data.

    Returns:
        dataframe with the read in data
    """

    if data_path is None:
        _data_path = os.path.join(os.path.join(GLOBAL_PWD, "..", ".."), DATA_FOLDER)
    else:
        _data_path = data_path

    raw_usage = create_dataframe(_data_path)
    last_update = read_timestamp(os.path.join(_data_path, TIMESTAMP_FILE))

    return raw_usage, last_update


def get_url_params(doc):
    """Reads in url parameters.

    Arguments:
        doc: a bokeh document to which elements can be added.

    Returns:
        A dictionary with the parsed url parameters
    """

    doc_args = doc.session_context.request.arguments

    return parse_url_params(doc_args)


def create_updates_tab():
    """
    Creates updates tab

    """

    file_path = os.path.join(os.path.join(GLOBAL_PWD, "..", ".."), UPDATES_FILE)

    updates_text = ""
    with open(file_path, "r", encoding=CONST_ENCODING) as myfile:
        updates_text = myfile.read()

    widget_updates = PreText(text="""%s""" % (updates_text))

    updates_widgets = column(children=[row(children=[widget_updates])])

    return Panel(child=updates_widgets, title="Release notes")


def create_about_tab():
    """
    Creates about tab

    """

    file_path = os.path.join(os.path.join(GLOBAL_PWD, "..", ".."), README_FILE)

    # about widget
    about_text = ""
    line_cnt = 0
    for line in open(file_path, "r", encoding=CONST_ENCODING):
        if not line.startswith("[!["):
            about_text += line
        line_cnt += 1

    widget_about = Div(text="""%s""" % (about_text), width=800)

    about_widgets = column(children=[row(children=[widget_about])])

    return Panel(child=about_widgets, title="About")


def create_usage_bar_plot():
    """ Creates a bar plot to show daily usage
    """

    bar_plot = figure(
        plot_height=400,
        plot_width=1200,
        title="",
        tools="pan, reset, save, wheel_zoom, crosshair, hover",
        x_axis_type="datetime",
        tooltips=[
            (CONST_COL_NAME_DATE, "@Date_str"),
            (CONST_COL_NAME_COST, "@Cost{$0.2f}"),
        ],
        min_border_bottom=75,
        min_border_left=70,
    )

    bar_plot.xaxis.formatter = DatetimeTickFormatter(
        hours=["%d %B %Y"], days=["%d %B %Y"], months=["%d %B %Y"], years=["%d %B %Y"],
    )

    bar_plot.xaxis.major_label_orientation = pi / 4
    bar_plot.yaxis.major_label_text_font_size = "12pt"

    return bar_plot


def create_top_services_pie_plot():
    """ Creates top services pie plot
    """

    pie_plot = figure(
        plot_height=500,
        plot_width=800,
        x_range=(-0.5, 1.0),
        tools="hover",
        tooltips=[
            (CONST_COL_NAME_SERVICE, "@Service"),
            (CONST_COL_NAME_COST, "@Cost{$0.2f}"),
            (CONST_COL_NAME_PERC, "@Perc{%0.2f}"),
        ],
    )

    return pie_plot


###### NO UNIT TESTS FOR ALL THE FOLLWING FUNCTIONS


def modify_doc(doc):
    """Main method to create a bokeh document

    Arguments:
        doc: a bokeh document to which elements can be added.

    """
    global GLOBAL_RAW_USAGE
    global GLOBAL_LAST_UPDATE

    # get the url parameters
    url_params = get_url_params(doc)

    # reads in the raw usage data
    GLOBAL_RAW_USAGE, GLOBAL_LAST_UPDATE = readin_data()

    # initialises data sources
    initiliase_data_sources()

    # sets the layout of the webapp
    _set_layout(doc, url_params)

    # plots the data
    _update_data(doc, url_params)

    # changing title
    doc.title = DEFAULT_REPORT_NAME


def initiliase_data_sources():
    """
    Initialises data sources
    """

    global GLOBAL_RAW_USAGE
    global GLOBAL_SUB_RAW_USAGE
    global GLOBAL_SUB_SERVICE_GRP

    global GLOBAL_TOTAL_SOURCE
    global GLOBAL_TOP_SERVICE_SOURCE

    default_subid = ""

    prep_sub_ids_list = prep_sub_ids(default_subid)

    GLOBAL_SUB_RAW_USAGE = get_data_for_subid(GLOBAL_RAW_USAGE, prep_sub_ids_list)

    sub_raw_usage_grp = group_day(GLOBAL_SUB_RAW_USAGE, add_missing_days=True)

    GLOBAL_TOTAL_SOURCE = ColumnDataSource(data=sub_raw_usage_grp)

    # Generates a data frame of top services which costed more than min_cost,
    #   rest of the costs added as Other
    GLOBAL_SUB_SERVICE_GRP = get_top_services(GLOBAL_SUB_RAW_USAGE)

    # calculate percentages for the top services
    GLOBAL_SUB_SERVICE_GRP = calc_top_services_perc(GLOBAL_SUB_SERVICE_GRP)

    # set the data source object
    GLOBAL_TOP_SERVICE_SOURCE = ColumnDataSource(data=GLOBAL_SUB_SERVICE_GRP)


def _update_data(*_):
    """
    Updates data
    """

    global GLOBAL_RAW_USAGE
    global GLOBAL_TOTAL_SOURCE
    global GLOBAL_TOP_SERVICE_SOURCE

    global GLOBAL_WIDGET_SUBID
    global GLOBAL_DATE_PICKER_FROM
    global GLOBAL_DATE_PICKER_TO
    global GLOBAL_WIDGET_SUBSCRIPTION_NAMES
    global GLOBAL_WIDGET_TOTAL_TEXT
    global GLOBAL_WIDGET_TOP_SERVICES_RB

    all_mode = False

    if GLOBAL_WIDGET_SUBID.value.upper() == "ALLMODE":
        all_mode = True
        new_sub_raw_usage = GLOBAL_RAW_USAGE.copy(deep=True)
        prep_sub_ids_list = new_sub_raw_usage["SubscriptionGuid"].unique()
    else:
        prep_sub_ids_list = prep_sub_ids(GLOBAL_WIDGET_SUBID.value.upper())
        new_sub_raw_usage = get_data_for_subid(GLOBAL_RAW_USAGE, prep_sub_ids_list)

    # Adjusting date interval
    if not new_sub_raw_usage.empty:

        date_st = pd.Timestamp(GLOBAL_DATE_PICKER_FROM.value)
        date_end = pd.Timestamp(GLOBAL_DATE_PICKER_TO.value)

        new_sub_raw_usage = new_sub_raw_usage.loc[
            (new_sub_raw_usage.Date >= date_st) & (new_sub_raw_usage.Date <= date_end)
        ]

    # For each subscription get the most recently used name in the selected time period
    # and show in UI
    subscription_names = []
    subscription_names_string = ""

    if not all_mode:
        for sub_id in prep_sub_ids_list:
            single_sub_usage = new_sub_raw_usage[
                (new_sub_raw_usage.SubscriptionGuid == sub_id)
            ].sort_values(by=["Date"], ascending=False)
            if single_sub_usage.empty:
                pass
            else:
                subscription_name = single_sub_usage.iloc[0].SubscriptionName
                subscription_names.append(subscription_name)

        if subscription_names:
            subscription_names_string = ", ".join(subscription_names)

    if all_mode:
        GLOBAL_WIDGET_SUBSCRIPTION_NAMES.text = "<b>{0} subscriptions selected</b>".format(
            len(prep_sub_ids_list)
        )
    else:
        GLOBAL_WIDGET_SUBSCRIPTION_NAMES.text = "<b>{0} subscriptions selected:</b> {1}".format(
            len(subscription_names), subscription_names_string
        )

    # TOTAL USAGE
    new_sub_raw_usage_grp = group_day(new_sub_raw_usage, add_missing_days=True)

    GLOBAL_TOTAL_SOURCE.data = dict(ColumnDataSource(data=new_sub_raw_usage_grp).data)

    # Ploting TOP SERVICES
    new_sub_service_grp = get_top_services(
        new_sub_raw_usage, top_services_grp_md=GLOBAL_WIDGET_TOP_SERVICES_RB.active
    )

    new_sub_service_grp_cnt = len(new_sub_service_grp)

    if not new_sub_raw_usage.empty and not new_sub_service_grp.empty:

        new_sub_service_grp[CONST_COL_NAME_ANGLE] = (
            new_sub_service_grp[CONST_COL_NAME_COST]
            / new_sub_service_grp[CONST_COL_NAME_COST].sum()
            * 2
            * pi
        )

        if new_sub_service_grp_cnt > 2:
            new_sub_service_grp["color"] = Category20c[new_sub_service_grp_cnt]
        else:
            new_sub_service_grp["color"] = Category20c[3][:new_sub_service_grp_cnt]
    else:
        new_sub_service_grp[CONST_COL_NAME_ANGLE] = 0
        new_sub_service_grp["color"] = Category20c[3][:1]

    GLOBAL_TOP_SERVICE_SOURCE.data = dict(
        ColumnDataSource(data=new_sub_service_grp).data
    )

    GLOBAL_WIDGET_TOTAL_TEXT.text = "Total usage: ${:,.2f}".format(
        new_sub_raw_usage_grp.sum()[CONST_COL_NAME_COST]
    )

    _plot_total_usage()

    _plot_top_services()


def _create_analysis_tab(doc, url_params):
    """
    Creates analysis tab

    Arguments:
        doc: a bokeh document to which elements can be added.
        url_params: url parameters passed with the url
    """

    global GLOBAL_WIDGET_SUBID
    global GLOBAL_DATE_PICKER_FROM
    global GLOBAL_DATE_PICKER_TO
    global GLOBAL_WIDGET_SUBSCRIPTION_NAMES
    global GLOBAL_WIDGET_TOTAL_TEXT
    global GLOBAL_WIDGET_TOP_SERVICES_RB

    global GLOBAL_S1
    global GLOBAL_S2

    global GLOBAL_RAW_USAGE
    global GLOBAL_LAST_UPDATE
    global GLOBAL_SUB_RAW_USAGE

    widget_input_text = Div(
        text=url_params[URL_PARAM_REPORT], style={"font-size": "200%", "color": "black"}
    )

    if GLOBAL_LAST_UPDATE is not None:
        last_update_text = Div(
            text="Last updated: {}".format(
                GLOBAL_LAST_UPDATE.strftime("%B %d, %Y, %r")
            ),
            style={"font-size": "125%", "color": "black"},
        )
    else:
        last_update_text = Div(text="Last updated:")

    GLOBAL_WIDGET_SUBID = TextInput(
        title="Subscription IDs (comma separated)",
        value=url_params[URL_PARAM_SUB_IDS],
        css_classes=["customTextInput"],
    )

    if not url_params[URL_PARAM_DT_FROM]:
        if not GLOBAL_SUB_RAW_USAGE.empty:
            date_min = GLOBAL_SUB_RAW_USAGE.Date.min().date()
        elif not GLOBAL_RAW_USAGE.empty:
            date_min = GLOBAL_RAW_USAGE.Date.min().date()
        else:
            date_min = pd.to_datetime("2016-01-01").date()
    else:
        date_min = url_params[URL_PARAM_DT_FROM].date()

    if not url_params[URL_PARAM_DT_TO]:
        if not GLOBAL_SUB_RAW_USAGE.empty:
            date_max = GLOBAL_SUB_RAW_USAGE.Date.min().date()
        elif not GLOBAL_RAW_USAGE.empty:
            date_max = GLOBAL_RAW_USAGE.Date.max().date()
        else:
            date_max = pd.to_datetime("2021-12-31").date()
    else:
        date_max = url_params[URL_PARAM_DT_TO].date()

    GLOBAL_DATE_PICKER_FROM = DatePicker(value=date_min, title="Date from")
    GLOBAL_DATE_PICKER_TO = DatePicker(value=date_max, title="Date to")

    GLOBAL_WIDGET_SUBSCRIPTION_NAMES = Div(
        text="", style={"font-size": "100%", "color": "black"}
    )

    widget_usage_text = Div(
        text="Usage ($):", style={"font-size": "150%", "color": "black"}
    )

    GLOBAL_S1 = create_usage_bar_plot()

    GLOBAL_WIDGET_TOTAL_TEXT = Div(
        text="Total usage: ${:,.2f}".format(0),
        style={"font-size": "200%", "color": "blue"},
    )

    widget_top_services_text = Div(
        text="Top services:", style={"font-size": "150%", "color": "black"}
    )

    # top services grouping button
    GLOBAL_WIDGET_TOP_SERVICES_RB = RadioButtonGroup(
        labels=[CONST_RB_LABEL_0, CONST_RB_LABEL_1, CONST_RB_LABEL_2, CONST_RB_LABEL_3],
        active=CONST_RB_DEFAULT,
    )

    # top services pie plot
    GLOBAL_S2 = create_top_services_pie_plot()
    top_services_table = _create_top_services_tbl()

    analysis_widgets = layout(
        [
            layout([widget_input_text, last_update_text]),
            [GLOBAL_WIDGET_SUBID, GLOBAL_DATE_PICKER_FROM, GLOBAL_DATE_PICKER_TO],
            [GLOBAL_WIDGET_SUBSCRIPTION_NAMES],
            [widget_usage_text],
            [GLOBAL_S1],
            [GLOBAL_WIDGET_TOTAL_TEXT],
            [widget_top_services_text],
            [GLOBAL_S2, [GLOBAL_WIDGET_TOP_SERVICES_RB, top_services_table]],
        ],
        sizing_mode="scale_width",
    )

    for widget in [GLOBAL_WIDGET_SUBID, GLOBAL_DATE_PICKER_FROM, GLOBAL_DATE_PICKER_TO]:
        widget.on_change("value", lambda attr, old, new: _update_data(doc, url_params))

    GLOBAL_WIDGET_TOP_SERVICES_RB.on_change(
        "active", lambda attr, old, new: _update_data(doc, url_params)
    )

    return Panel(child=analysis_widgets, title="Analysis")


def _create_top_services_tbl():
    """ Creates top services table
    """

    global GLOBAL_SUB_SERVICE_GRP
    global GLOBAL_TOP_SERVICE_SOURCE

    # Top services table
    cols = []
    for col in GLOBAL_SUB_SERVICE_GRP.columns:

        if col == CONST_COL_NAME_COST:
            cols.append(
                TableColumn(
                    field=col,
                    title=col,
                    formatter=NumberFormatter(
                        format="$0,0[.]00", text_align="right", language="it"
                    ),
                    width=100,
                )
            )
        elif col == CONST_COL_NAME_PERC:
            cols.append(
                TableColumn(
                    field=col,
                    title=col,
                    formatter=NumberFormatter(
                        format="0,0[.]00%", text_align="right", language="it"
                    ),
                    width=50,
                )
            )
        elif col in [CONST_COL_NAME_ANGLE, "color"]:
            continue
        else:
            cols.append(TableColumn(field=col, title=col))

    top_services_table = DataTable(
        columns=cols, source=GLOBAL_TOP_SERVICE_SOURCE, width=400
    )

    return top_services_table


def _set_layout(doc, url_params):
    """Sets the layout of the document.

    Arguments:
        doc: a bokeh document to which elements can be added.
        url_params: parameters passed with the url
    """

    tabs = Tabs(
        tabs=[
            _create_analysis_tab(doc, url_params),
            create_updates_tab(),
            create_about_tab(),
        ]
    )

    _plot_total_usage()

    _plot_top_services()

    doc.add_root(tabs)


def _plot_total_usage():
    """Plots total usgae by the subscription.

    """

    global GLOBAL_S1
    global GLOBAL_TOTAL_SOURCE

    GLOBAL_S1.vbar(
        x=CONST_COL_NAME_DATE,
        top=CONST_COL_NAME_COST,
        width=8.64e7 * 0.9,
        source=GLOBAL_TOTAL_SOURCE,
    )

    GLOBAL_S1.y_range.start = 0


def _plot_top_services():
    """Plots top services pie chart
    """
    global GLOBAL_S2
    global GLOBAL_TOP_SERVICE_SOURCE

    GLOBAL_S2.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum(CONST_COL_NAME_ANGLE, include_zero=True),
        end_angle=cumsum(CONST_COL_NAME_ANGLE),
        line_color="white",
        fill_color="color",
        legend_field=CONST_COL_NAME_SERVICE,
        source=GLOBAL_TOP_SERVICE_SOURCE,
    )

    GLOBAL_S2.legend.location = "top_right"
    GLOBAL_S2.legend.label_width = 180
    GLOBAL_S2.legend.label_text_font_size = "8pt"

    GLOBAL_S2.axis.axis_label = None
    GLOBAL_S2.axis.visible = False
    GLOBAL_S2.grid.grid_line_color = None
