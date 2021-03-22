"""
Azure usage analysis webapp
"""
import argparse

from src_webapp.server import bk_worker


def setup():
    """
    Prepared arguments for the command line
    """

    parser = argparse.ArgumentParser(
        description="Flask webframework with embedded Bokeh app."
    )

    parser.add_argument(
        "-b", "--bport", help="The port of the Bokeh webapp", default=5001
    )
    parser.add_argument(
        "-o",
        "--origin",
        help="The origin of the websocket connections",
        default="127.0.0.1",
    )

    return parser.parse_args()


if __name__ == "__main__":

    # Reading in the command line arguments
    ARGS = setup()

    # Running Bokeh server
    bk_worker(ARGS.origin, ARGS.bport)
