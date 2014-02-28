"""
Various functions which can be used in all other modules.
"""

def check_missing_params(method_name, **kwargs):
    missing_params = []
    for param, value in enumerate(kwargs):
        if value is None:
            missing_params.append(param)
    if missing_params:
        raise ValueError("Missing parameters while calling {}: {}".format(method_name, missing_params))

