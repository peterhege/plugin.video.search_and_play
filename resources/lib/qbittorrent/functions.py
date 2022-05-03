import re

try:
    from typing import Union, Match
except:
    pass


def to_snake_case(camel_case):  # type: (str) -> str
    def variable_replace(match):  # type: (Match) -> str
        return '_{}'.format(match.group(0).lower())

    return re.sub(r'([A-Z])', variable_replace, camel_case)
