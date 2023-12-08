from pathlib import Path
import random
import string


def generate_code(length=4):
    """
    Generate a random alphanumeric code of a given length.

    The function generates a random code consisting
    of uppercase letters and digits.
    By default, the length of the code is 4, but it can
    be adjusted by providing a different length as an argument.

    Parameters:
    length (int, optional): The length of the generated code. Defaults to 4.

    Returns:
    str: A random alphanumeric code of the specified length.

    Example:
    >>> generate_code()
    'A3F2'
    >>> generate_code(6)
    'B4T9Z2'
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


CODE = generate_code()
PARENT_DIR = Path(__file__).parent.parent
BASE_DIR = PARENT_DIR / CODE
DATA_DIR = BASE_DIR / "Property"
OUTPUT_DIR = BASE_DIR / "zz_python_do_not_touch"
OUTPUT_DIRx = BASE_DIR / "Cadd" / "map_imports"
FORM_DIR = BASE_DIR / "PM"
LOG_DIR = PARENT_DIR / "logs"
INPUT_DIR = PARENT_DIR / "inputs"
TMP_DIR = PARENT_DIR / "tmp"
TEMPLATE_DIR = PARENT_DIR / "templates"
CADD_DIR = BASE_DIR / "Cadd"
RESULT_DIR = PARENT_DIR / "output"
