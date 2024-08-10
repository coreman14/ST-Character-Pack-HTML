"Tests to make sure the html is updated with the correct arguments"
from argparse import Namespace

import html_arg_functions
from html_main import HTML_SNIP2


def test_outfitHeight():
    "Test if the pages outfit height is updated"
    test_args = Namespace(outfitheight=300)
    assert HTML_SNIP2 != html_arg_functions.update_html(test_args, HTML_SNIP2)


def test_accessoryHeight():
    "Test the pages accessory height is updated"
    test_args = Namespace(accessoryheight=300)
    assert HTML_SNIP2 != html_arg_functions.update_html(test_args, HTML_SNIP2)
