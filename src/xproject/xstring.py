import re


def camel_to_snake(string: str) -> str:
    """
    >>> camel_to_snake('CamelCaseString')
    'camel_case_string'

    """
    string = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    string = re.sub("([a-z0-9])([A-Z])", r"\1_\2", string).lower()
    return string


def snake_to_camel(string: str) -> str:
    """
    >>> snake_to_camel('snake_case_string')
    'SnakeCaseString'

    """
    return "".join(i.capitalize() for i in string.split("_"))


if __name__ == '__main__':
    print(camel_to_snake("CamelCaseString"))
    print(snake_to_camel("snake_case_string"))
