from argparse import Namespace

import html_arg_functions
from html_main import html_snip2


def test_outfitHeight():
    test_args = Namespace(outfitheight=300)
    assert html_snip2 != html_arg_functions.update_html(test_args, html_snip2)


def test_accessoryHeight():
    test_args = Namespace(accessoryheight=300)
    assert html_snip2 != html_arg_functions.update_html(test_args, html_snip2)
