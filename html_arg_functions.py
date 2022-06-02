from argparse import Namespace


def update_html_arg_snip2(args: Namespace, string_to_replace: str):
    """
    Updates the the string_to_replace with a namespace.

    This function will check if the attribute is set before trying to replace
    """
    if hasattr(args, "backgroundimage") and args.backgroundimage:
        args.backgroundimage = args.backgroundimage.replace("\\", "/")
        string_to_replace = string_to_replace.replace(
            "background-color: White; /*Background Replace*/",
            f'background-color: White; /*Background Replace*/background-image: url("{args.backgroundimage}"); /*Background Replace*/',
        )
    if hasattr(args, "backgroundcolor") and args.backgroundcolor:
        string_to_replace = string_to_replace.replace(
            "background-color: White; /*Background Replace*/",
            f"background-color: {args.backgroundcolor}; /*Background Replace*/",
        )

    if hasattr(args, "toppadding") and args.toppadding:
        string_to_replace = string_to_replace.replace(
            ".characterswrap{",
            f".characterswrap{{ padding-top: {args.toppadding}px;",
        )
    if hasattr(args, "titlecolor") and args.titlecolor:
        string_to_replace = string_to_replace.replace(
            "#title{",
            f"#title{{ color: {args.titlecolor};",
        )
    if hasattr(args, "charactercolor") and args.charactercolor:
        string_to_replace = string_to_replace.replace(
            ".character{",
            f".character{{ background-color: {args.charactercolor};",
        )
    return string_to_replace


def update_html_arg_snip3(args: Namespace, string_to_replace: str):
    """
    Updates the the string_to_replace with a namespace.

    This function will check if the attribute is set before trying to replace
    """
    if hasattr(args, "color2") and args.color2:
        string_to_replace = string_to_replace.replace(
            'context.fillStyle="#121212"; /*Color2 replace*/',
            f'context.fillStyle="{args.color2}"; /*Color2 replace*/',
        )
    if hasattr(args, "color1") and args.color1:
        string_to_replace = string_to_replace.replace(
            'context.fillStyle="Black"; /*Color1 replace*/',
            f'context.fillStyle="{args.color1}"; /*Color1 replace*/',
        )

    if hasattr(args, "rectbackgroundcolor") and args.rectbackgroundcolor:
        string_to_replace = string_to_replace.replace(
            'context.fillStyle="White"; /*rect color*/',
            f'context.fillStyle="{args.rectbackgroundcolor}"; /*rect color*/',
        )
    if hasattr(args, "textcolor") and args.textcolor:
        string_to_replace = string_to_replace.replace(
            'context.fillStyle="Black"; /*text color*/',
            f'context.fillStyle="{args.textcolor}"; /*text color*/',
        )

    return string_to_replace
