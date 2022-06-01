from argparse import Namespace

import html_arg_functions
from html_main import html_snip1, html_snip2, html_snip3


def test_backgroundimage():
    test_args = Namespace(backgroundimage="test.png")
    assert html_snip2 != html_arg_functions.update_html_arg_snip2(test_args, html_snip2)


def test_backgroundcolor():
    test_args = Namespace(backgroundcolor="#111111")
    assert html_snip2 != html_arg_functions.update_html_arg_snip2(test_args, html_snip2)


def test_toppadding():
    test_args = Namespace(toppadding=11)
    assert html_snip2 != html_arg_functions.update_html_arg_snip2(test_args, html_snip2)


def test_titlecolor():
    test_args = Namespace(titlecolor="#123456")
    assert html_snip2 != html_arg_functions.update_html_arg_snip2(test_args, html_snip2)


def test_charactercolor():
    test_args = Namespace(charactercolor="#999999")
    assert html_snip2 != html_arg_functions.update_html_arg_snip2(test_args, html_snip2)


def test_rectbackgroundcolor():
    test_args = Namespace(rectbackgroundcolor="#123456")
    assert html_snip3 != html_arg_functions.update_html_arg_snip3(test_args, html_snip3)


def test_textcolor():
    test_args = Namespace(textcolor="#111111")
    assert html_snip3 != html_arg_functions.update_html_arg_snip3(test_args, html_snip3)


def test_color2():
    test_args = Namespace(color2="#123456")
    assert html_snip3 != html_arg_functions.update_html_arg_snip3(test_args, html_snip3)


def test_color1():
    test_args = Namespace(color1="#123456")
    assert html_snip3 != html_arg_functions.update_html_arg_snip3(test_args, html_snip3)
