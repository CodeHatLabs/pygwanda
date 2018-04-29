from random import choice
from time import gmtime


# Omit "lIO10" (lowercase ell, uppercase eye and oh, digits one and zero)
#   for reliable human readability.
UNAMBIGUOUS_LOWER = 'qwertyuiopasdfghjkzxcvbnm'
UNAMBIGUOUS_UPPER = 'QWERTYUPASDFGHJKLZXCVBNM'
UNAMBIGUOUS_DIGITS = '23456789'
UNAMBIGUOUS_SYMBOLS = '~!@#$%^&*()_-+=[]{};:<>,.?/'
UNAMBIGUOUS_ALPHA = UNAMBIGUOUS_LOWER + UNAMBIGUOUS_UPPER
UNAMBIGUOUS_ALPHANUM = UNAMBIGUOUS_ALPHA + UNAMBIGUOUS_DIGITS
UNAMBIGUOUS_ASCII = UNAMBIGUOUS_ALPHANUM + UNAMBIGUOUS_SYMBOLS


def gmtime_string(timeparts=None):
    if not timeparts:
        timeparts = gmtime()
    return '%4d%02d%02dT%02d%02d%02dZ' % timeparts[:6]


def random_unambiguous_string(length=10, characters=UNAMBIGUOUS_ASCII):
    return choice(characters) \
        + ''.join([choice(characters) for x in range(length - 1)])


