from argparse import Namespace


def update_html(args: Namespace, string_to_replace: str):
    """
    Updates the the string_to_replace with a namespace.

    This function will check if the attribute is set before trying to replace
    """
    if hasattr(args, "outfitheight") and args.outfitheight:
        string_to_replace = string_to_replace.replace(
            "height: 200px; /*Main Height replace*/",
            f"height: {args.outfitheight}px; /*Main Height replace*/",
        )
    if hasattr(args, "accessoryheight") and args.accessoryheight:
        string_to_replace = string_to_replace.replace(
            "height: 400px; /*Access Height replace*/",
            f"height: {args.accessoryheight}px; /*Access Height replace*/",
        )
    return string_to_replace
