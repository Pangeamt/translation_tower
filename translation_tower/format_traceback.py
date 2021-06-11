import traceback


def format_traceback(e):
    stack = traceback.extract_stack() + traceback.extract_tb(e.__traceback__)  # add limit=??
    pretty = traceback.format_list(stack)
    return ''.join(pretty) + '\n  {} {}'.format(e.__class__, e)
