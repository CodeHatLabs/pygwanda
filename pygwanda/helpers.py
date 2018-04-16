from random import choice


# Omit "lIO10" (lowercase ell, uppercase eye and oh, numbers one and zero)
#   for reliable human readability.
UNAMBIGUOUS_ALPHA = 'qwertyuiopasdfghjkzxcvbnm' \
                    'QWERTYUPASDFGHJKLZXCVBNM'
UNAMBIGUOUS_ASCII = UNAMBIGUOUS_ALPHA \
                    + \
                    '23456789' \
                    '~!@#$%^&*()_-+=[]{};:<>,.?/'


def random_unambiguous_ascii_string(length=10):
    return choice(UNAMBIGUOUS_ALPHA) \
        + ''.join([choice(UNAMBIGUOUS_ASCII) for x in range(length - 1)])


