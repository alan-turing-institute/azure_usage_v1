import matplotlib.pyplot as plt

from ..src_webapp.constants import (
    CONST_COL_NAME_YM,
    CONST_COL_NAME_COST,
    CONST_COL_NAME_IDEALCOST,
    CONST_COL_NAME_AVAILCOST,
    CONST_COL_NAME_YM,
)


def plot_year_month_bar_stacked_ext(spnsr_df, ea_df, ylim=None):
    """Plots costs on a montly basis

    Args:
        spnsr_raw_data_gr_df: a dataframe with two columns: Year-Month and Cost representing raw
            expenditure for the sponsorhip account

        ea_raw_data_gr_df: a dataframe with two columns: Year-Month and Cost representing raw
            expenditure for the ea accounts

    """

    width = 0.5

    fig = plt.figure(figsize=(9, 6), dpi=300)
    ax = fig.add_subplot(111)

    # Ideal Sponsorship + EA usage
    ax.plot(
        spnsr_df[CONST_COL_NAME_YM],
        spnsr_df[CONST_COL_NAME_IDEALCOST] + ea_df[CONST_COL_NAME_IDEALCOST],
        linewidth=2,
        markersize=6,
        marker="o",
        label="Optimum sponsorship + ea usage",
        color="chocolate",
        linestyle="dashed",
    )

    # Ideal sponsorship usage
    ax.plot(
        spnsr_df[CONST_COL_NAME_YM],
        spnsr_df[CONST_COL_NAME_IDEALCOST],
        linewidth=2,
        markersize=6,
        marker="o",
        label="Optimum sponsorship usage",
        color="black",
        linestyle="dashed",
    )
    # Available Sponsorship + EA usage
    ax.plot(
        ea_df[CONST_COL_NAME_YM],
        spnsr_df[CONST_COL_NAME_AVAILCOST] + ea_df[CONST_COL_NAME_AVAILCOST],
        linewidth=2,
        markersize=6,
        marker="o",
        label="Available sponsorship + ea usage",
        color="orange",
        linestyle="solid",
    )

    # Available sponsorship usage
    ax.plot(
        spnsr_df[CONST_COL_NAME_YM],
        spnsr_df[CONST_COL_NAME_AVAILCOST],
        linewidth=2,
        markersize=6,
        marker="o",
        label="Available sponsorship usage",
        color="blue",
        linestyle="solid",
    )

    # Sponsorship usage
    spnsr_p = ax.bar(
        spnsr_df[CONST_COL_NAME_YM].values,
        spnsr_df[CONST_COL_NAME_COST],
        width,
        label="Actual sponsorship acc usage",
    )

    # EA usage
    ea_p = ax.bar(
        ea_df[CONST_COL_NAME_YM].values,
        ea_df[CONST_COL_NAME_COST],
        width,
        label="EA acc usage",
        bottom=spnsr_df[CONST_COL_NAME_COST],
    )

    ax.set_xlabel("Year-Month", fontsize=20)
    ax.set_xticklabels(spnsr_df["Year-Month"].values, rotation=45)

    if ylim is not None:
        ax.set_ylim(0, ylim)

    ax.set_ylabel("Monthly usage ($)", fontsize=20)

    ax.grid()
    ax.legend()

    # ax.axvspan(-1, 8.5, facecolor='0.33', alpha=0.1)

    ax.set_xlim(-0.5, 11.5)

    fig.tight_layout()
