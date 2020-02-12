import pandas as pd
import os
from math import pi

# azure_usage imports
from .constants import (
    DATA_DT_FROM,
    DATA_DT_TO,
    CONST_COL_NAME_COST,
    CONST_COL_NAME_SERVICE,
    CONST_COL_NAME_ANGLE,
    CONST_COL_NAME_PERC,
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
    TIMESTAMP_FILE
)

from .subs import (
    get_data_for_subid, 
    get_top_services,
    calc_top_services_perc)

from .totals import group_day
from .utilities import prep_sub_ids, parse_url_params, read_timestamp
from .data_loader import create_dataframe

# Bokeh imports
from bokeh.embed import server_document, components
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure
from bokeh.themes import Theme
from bokeh.transform import factor_cmap
from bokeh.core.properties import value
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from bokeh.models.widgets import Select, Slider, TextInput, DateRangeSlider, \
    DataTable, DateFormatter, TableColumn, NumberFormatter, Div, DatePicker, \
    Tabs, Panel, PreText, RadioButtonGroup
from bokeh.models.glyphs import Wedge

# Global variables
global_raw_usage = None
global_last_update = None
global_sub_raw_usage = None
global_sub_service_grp = None

global_total_source = None

global_widget_subid = TextInput()
global_date_picker_from = None
global_date_picker_to = None
global_widget_subscription_names = None
global_widget_total_text = None
global_widget_top_services_rb = None

global_s1 = None
global_s2 = None

global_top_service_source = None

global_pwd = os.path.dirname(os.path.realpath(__file__))

def readin_data(data_path=None):
    """ Reads in raw Azure usage data.

    Returns:
        dataframe with the read in data
    """

    if data_path is None:
        _data_path = os.path.join(
            os.path.join(global_pwd, '..', '..'), 
            DATA_FOLDER)
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

    file_path = os.path.join(
        os.path.join(global_pwd, '..', '..'),
        UPDATES_FILE)

    updates_text = ""
    with open(file_path, "r", encoding=CONST_ENCODING) as myfile:
        updates_text = myfile.read()

    widget_updates = PreText(text="""%s""" % (updates_text))

    updates_widgets = column(children=[
        row(children=[widget_updates])
    ])

    return Panel(child=updates_widgets, title = "Release notes")

def create_about_tab():
    """
    Creates about tab

    """

    file_path = os.path.join(
        os.path.join(global_pwd, '..', '..'), 
        README_FILE)
    
    # about widget
    about_text = ""
    line_cnt = 0
    for line in open(file_path, "r", encoding=CONST_ENCODING):
        if line_cnt > 3:
            about_text += line
        line_cnt += 1

    widget_about = PreText(text="""%s""" % (about_text))

    about_widgets = column(children=[
        row(children=[widget_about])
    ])

    return Panel(child=about_widgets, title = "About")

def create_usage_bar_plot():
    """ Creates a bar plot to show daily usage
    """

    bar_plot = figure(plot_height=400, plot_width=1200, title="",
        tools="pan, reset, save, wheel_zoom, crosshair, hover",
        x_axis_type = "datetime",
        tooltips=[("Date", '@Date{%F}'), (CONST_COL_NAME_COST, '@Cost{$0.2f}')])

    bar_plot.hover.formatters={'Date': 'datetime'}

    bar_plot.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )

    bar_plot.xaxis.major_label_orientation = pi/2

    return bar_plot

def create_top_services_pie_plot():
    """ Creates top services pie plot
    """
    
    pie_plot = figure(plot_height=500, plot_width=800, x_range=(-0.5, 1.0),
        tools='hover', tooltips=[(CONST_COL_NAME_SERVICE, '@Service'),
            (CONST_COL_NAME_COST, '@Cost{$0.2f}'),
            (CONST_COL_NAME_PERC, '@Perc{%0.2f}')
        ])

    return pie_plot

###### NO UNIT TESTS FOR ALL THE FOLLWING FUNCTIONS

def modify_doc(doc):
    """Main method to create a bokeh document

    Arguments:
        doc: a bokeh document to which elements can be added.

    """
    global global_raw_usage
    global global_last_update

    # get the url parameters
    url_params = get_url_params(doc)

    # reads in the raw usage data
    global_raw_usage, global_last_update = readin_data()

    # initialises data sources
    initiliase_data_sources()

    # sets the layout of the webapp
    _set_layout(doc, url_params)
    
    # plots the data
    _update_data(doc, url_params)

    # changing title
    doc.title = DEFAULT_REPORT_NAME

def initiliase_data_sources():
    
    global global_raw_usage
    global global_sub_raw_usage
    global global_sub_service_grp

    global global_total_source
    global global_top_service_source

    default_subid = "" 

    prep_sub_ids_list = prep_sub_ids(default_subid)
    
    global_sub_raw_usage = get_data_for_subid(global_raw_usage, prep_sub_ids_list)

    sub_raw_usage_grp = group_day(global_sub_raw_usage, add_missing_days=True)

    global_total_source = ColumnDataSource(data=sub_raw_usage_grp)
    
    # Generates a data frame of top services which costed more than min_cost,
    #   rest of the costs added as Other
    global_sub_service_grp = get_top_services(global_sub_raw_usage)

    # calculate percentages for the top services
    global_sub_service_grp = calc_top_services_perc(global_sub_service_grp)

    # set the data source object
    global_top_service_source = ColumnDataSource(data=global_sub_service_grp)

def _update_data(doc, url_params):
    """
    
    Arguments:
        doc: a bokeh document to which elements can be added.
        url_params: parameters passed with the url
        raw_usage: raw usage dataframe

    """
    
    global global_raw_usage
    global global_total_source
    global global_top_service_source

    global global_widget_subid
    global global_date_picker_from
    global global_date_picker_to
    global global_widget_subscription_names
    global global_widget_total_text
    global global_widget_top_services_rb

    all_mode = False

    if global_widget_subid.value.upper() == "ALLMODE":
        all_mode = True
        new_sub_raw_usage = global_raw_usage.copy(deep=True)
        prep_sub_ids_list = new_sub_raw_usage['SubscriptionGuid'].unique()
    else:
        prep_sub_ids_list = prep_sub_ids(global_widget_subid.value.upper())
        new_sub_raw_usage = get_data_for_subid(global_raw_usage, prep_sub_ids_list)

    # Adjusting date interval
    if not new_sub_raw_usage.empty:

        date_st = pd.Timestamp(global_date_picker_from.value)
        date_end = pd.Timestamp(global_date_picker_to.value)

        new_sub_raw_usage = new_sub_raw_usage.loc[(new_sub_raw_usage.Date >= date_st) &
                                                  (new_sub_raw_usage.Date <= date_end)]

    # For each subscription get the most recently used name in the selected time period
    # and show in UI
    subscription_names = []
    subscription_names_string = ""

    if not all_mode:
        for sub_id in prep_sub_ids_list:
            single_sub_usage = new_sub_raw_usage[(new_sub_raw_usage.SubscriptionGuid == sub_id)].sort_values(by=['Date'],ascending=False)
            if(single_sub_usage.empty):
                pass
            else:
                subscription_name = single_sub_usage.iloc[0].SubscriptionName
                subscription_names.append(subscription_name)
        
        if(subscription_names):
            subscription_names_string = ", ".join(subscription_names)
            
    if all_mode:
        global_widget_subscription_names.text = "<b>{0} subscriptions selected</b>".format(len(prep_sub_ids_list))
    else:
        global_widget_subscription_names.text = "<b>{0} subscriptions selected:</b> {1}".format(len(subscription_names), subscription_names_string)
    
    # TOTAL USAGE
    new_sub_raw_usage_grp = group_day(new_sub_raw_usage, add_missing_days=True)

    global_total_source.data = ColumnDataSource(data=new_sub_raw_usage_grp).data

    # Ploting TOP SERVICES
    new_sub_service_grp = get_top_services(new_sub_raw_usage, top_services_grp_md=global_widget_top_services_rb.active)

    new_sub_service_grp_cnt = len(new_sub_service_grp)

    if not new_sub_raw_usage.empty and not new_sub_service_grp.empty:

        new_sub_service_grp[CONST_COL_NAME_ANGLE] = new_sub_service_grp[CONST_COL_NAME_COST]/new_sub_service_grp[CONST_COL_NAME_COST].sum() * 2*pi

        if new_sub_service_grp_cnt > 2:
            new_sub_service_grp['color'] = Category20c[new_sub_service_grp_cnt]
        else:
            new_sub_service_grp['color'] = Category20c[3][:new_sub_service_grp_cnt]
    else:
        new_sub_service_grp[CONST_COL_NAME_ANGLE] = 0
        new_sub_service_grp['color'] = Category20c[3][:1]

    global_top_service_source.data = ColumnDataSource(data=new_sub_service_grp).data

    global_widget_total_text.text = "Total usage: ${:,.2f}".format(new_sub_raw_usage_grp.sum()[CONST_COL_NAME_COST])

def _create_analysis_tab(doc, url_params):
    """
    Creates analysis tab
    
    Arguments:
        doc: a bokeh document to which elements can be added.
        url_params: url parameters passed with the url
    """

    global global_widget_subid
    global global_date_picker_from
    global global_date_picker_to
    global global_widget_subscription_names
    global global_widget_total_text
    global global_widget_top_services_rb

    global global_s1
    global global_s2

    global global_raw_usage
    global global_last_update
    global global_sub_raw_usage

    widget_input_text = Div(text=url_params[URL_PARAM_REPORT],
        style={'font-size': '200%', 'color': 'black'})

    if global_last_update is not None:
        last_update_text = Div(text="Last updated: {}".format(global_last_update.strftime('%B %d, %Y, %r')),
            style={'font-size': '125%', 'color': 'black'})
    else:
        last_update_text = None
    
    global_widget_subid = TextInput(title="Subscription IDs (comma separated)", value=url_params[URL_PARAM_SUB_IDS],
        css_classes=['customTextInput'])

    date_min = url_params[URL_PARAM_DT_FROM]

    if not date_min:
        if not global_sub_raw_usage.empty:
            date_min = global_sub_raw_usage.Date.min()
        elif not global_raw_usage.empty:
            date_min = global_raw_usage.Date.min()
        else:
            date_min = pd.to_datetime("2016-01-01")

    date_max = url_params[URL_PARAM_DT_TO]

    if not date_max:
        if not global_sub_raw_usage.empty:
            date_max = global_sub_raw_usage.Date.min()
        elif not global_raw_usage.empty:
            date_max = global_raw_usage.Date.max()
        else:
            date_max = pd.to_datetime("2021-12-31")

    global_date_picker_from = DatePicker(value=date_min, title="Date from")
    global_date_picker_to = DatePicker(value=date_max, title="Date to")

    global_widget_subscription_names = Div(text="",
        style={'font-size': '100%', 'color': 'black'})

    widget_usage_text = Div(text="Usage ($):",
        style={'font-size': '150%', 'color': 'black'})

    global_s1 = create_usage_bar_plot()

    global_widget_total_text = Div(text="Total usage: ${:,.2f}".format(0),
        style={'font-size': '200%', 'color': 'blue'})

    widget_top_services_text = Div(text="Top services:",
        style={'font-size': '150%', 'color': 'black'})

    # top services grouping button
    global_widget_top_services_rb = RadioButtonGroup(
        labels=[CONST_RB_LABEL_0, CONST_RB_LABEL_1, CONST_RB_LABEL_2, CONST_RB_LABEL_3], 
        active=CONST_RB_DEFAULT)

    # top services pie plot
    global_s2 = create_top_services_pie_plot()
    top_services_table = _create_top_services_tbl()

    analysis_widgets = layout([
        layout([widget_input_text, last_update_text]),
        [global_widget_subid, global_date_picker_from, global_date_picker_to],
        [global_widget_subscription_names],
        [widget_usage_text], 
        [global_s1],
        [global_widget_total_text],
        [widget_top_services_text],
        [global_s2, [global_widget_top_services_rb, top_services_table]]
    ], sizing_mode='scale_width')

    for w in [global_widget_subid, global_date_picker_from, global_date_picker_to]:
        w.on_change('value', lambda attr, old, new: _update_data(doc, url_params))

    global_widget_top_services_rb.on_change('active', lambda attr, old, new: _update_data(doc, url_params))

    return Panel(child=analysis_widgets, title = "Analysis")

def _create_top_services_tbl():
    """ Creates top services table
    """

    global global_sub_service_grp
    global global_top_service_source

    # Top services table
    Columns = []
    for Ci in global_sub_service_grp.columns:

        if (Ci == CONST_COL_NAME_COST):
            Columns.append(TableColumn(field=Ci, title=Ci,formatter=NumberFormatter(format='$0,0[.]00',text_align='right',language='it'), width=100))
        elif (Ci == CONST_COL_NAME_PERC):
            Columns.append(TableColumn(field=Ci, title=Ci,formatter=NumberFormatter(format='0,0[.]00%',text_align='right',language='it'), width=50))
        elif (Ci in [CONST_COL_NAME_ANGLE, "color"]):
            continue
        else:
            Columns.append(TableColumn(field=Ci, title=Ci))

    top_services_table = DataTable(columns=Columns, source=global_top_service_source, width=400)
    
    return top_services_table

def _set_layout(doc, url_params):
    """Sets the layout of the document.

    Arguments:
        doc: a bokeh document to which elements can be added.
        url_params: parameters passed with the url
    """

    tabs = Tabs(tabs=[
        _create_analysis_tab(doc, url_params),
        create_updates_tab(), 
        create_about_tab()])

    _plot_total_usage()

    _plot_top_services()

    doc.add_root(tabs)

def _plot_total_usage():
    """Plots total usgae by the subscription.

    """

    global global_s1
    global global_total_source

    global_s1.vbar(x="Date", top=CONST_COL_NAME_COST, width=8.64e+7*.9, source=global_total_source)
    global_s1.y_range.start = 0

def _plot_top_services():
    """Plots top services pie chart
    """
    global global_s2
    global global_top_service_source

    global_s2.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum(CONST_COL_NAME_ANGLE, include_zero=True), end_angle=cumsum(CONST_COL_NAME_ANGLE),
            line_color="white", fill_color='color', legend=CONST_COL_NAME_SERVICE, source=global_top_service_source)

    global_s2.axis.axis_label = None
    global_s2.axis.visible = False
    global_s2.grid.grid_line_color = None
