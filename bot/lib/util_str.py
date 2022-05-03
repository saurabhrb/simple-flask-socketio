from unidecode import unidecode
import re
import numbers
import string
import random


def clean_text(text, only_ascii=True):
    if text is None:
        return text
    elif isinstance(text, numbers.Number):
        return text
    else:
        if only_ascii:
            return unidecode(text).strip()
        else:
            return text.strip()


def is_empty(item):
    return item is None or str(item).strip() == ''


def valid_password_fmt(password, restrict_size=True, restrict_digit=True, restrict_caps=True):
    valid = True,
    err_msg = ''
    if restrict_size and len(password) < 8:
        valid = False
        err_msg = "Password must be at least 8 letters long"
    elif restrict_digit and re.search('[0-9]', password) is None:
            valid = False
            err_msg = "Password must contain at least 1 number in it"
    elif restrict_caps and re.search('[A-Z]', password) is None:
            valid = False
            err_msg = "Password must contain at least 1 capital letter"

    return valid, err_msg


def valid_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email)


def extract_pos_ints(text):
    """ Extracts Positive integers from the text"""
    return [int(s) for s in text.split() if s.isdigit()]


def extract_pos_nums(text):
    """Extract positive int/float from the text"""
    results = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    final_results = [float(i) for i in results]
    return final_results


def remove_consecutive_spaces(text):
    """Ex: ' My    Name  is   John\n is  ' -> 'My Name is John' (It also removes trailing and leading space/s)

    """
    return " ".join(text.split())


def generate_random_alphanumeric(size):
    letters = [each for each in string.ascii_lowercase]
    numbers = [str(i) for i in range(10)]

    choices = letters + numbers
    random.shuffle(choices)

    random_str = ''.join(random.choice(choices) for i in range(size))
    return random_str
