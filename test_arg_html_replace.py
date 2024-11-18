"Tests to make sure the html is updated with the correct arguments"
from argparse import Namespace

from create_html_js import update_html, read_base_html_file


def test_outfit_height():
    "Test if the pages outfit height is updated"
    test_args = Namespace(outfitheight=300)
    base_html = read_base_html_file()
    assert base_html != update_html(test_args, base_html)


def test_accessory_height():
    "Test the pages accessory height is updated"
    test_args = Namespace(accessoryheight=300)
    base_html = read_base_html_file()
    assert base_html != update_html(test_args, base_html)
