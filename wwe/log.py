import click


def set_verbose_mode(verbose_mode):
    """Set verbose mode value globally so that children functions can access it."""
    global verbose
    verbose = verbose_mode
