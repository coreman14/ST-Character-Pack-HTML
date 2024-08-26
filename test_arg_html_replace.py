"Tests to make sure the html is updated with the correct arguments"
from argparse import Namespace

import html_arg_functions
from html_main import HTML_SNIP1


def test_outfit_height():
    "Test if the pages outfit height is updated"
    test_args = Namespace(outfitheight=300)
    assert HTML_SNIP1 != html_arg_functions.update_html(test_args, HTML_SNIP1)


def test_accessory_height():
    "Test the pages accessory height is updated"
    test_args = Namespace(accessoryheight=300)
    assert HTML_SNIP1 != html_arg_functions.update_html(test_args, HTML_SNIP1)
