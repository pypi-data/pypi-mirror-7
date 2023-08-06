DEFAULT_SETTINGS = {
    'first': {
        'required': True,
        'allow_initials': True,
        'allow_prefix': True,
        'weight': 3,
    },
    'middle': {
        'required': False,
        'allow_initials': True,
        'allow_prefix': False,
        'weight': 2,
    },
    'last': {
        'required': True,
        'allow_initials': False,
        'allow_prefix': False,
        'weight': 5,
    },
}

STRICT_SETTINGS = {
    'first': {
        'required': True,
        'allow_initials': False,
        'allow_prefix': False,
        'weight': 3,
    },
    'middle': {
        'required': False,
        'allow_initials': False,
        'allow_prefix': False,
        'weight': 2,
    },
    'last': {
        'required': True,
        'allow_initials': False,
        'allow_prefix': False,
        'weight': 5,
    },
}

LENIENT_SETTINGS = {
    'first': {
        'required': False,
        'allow_initials': True,
        'allow_prefix': True,
        'weight': 3,
    },
    'middle': {
        'required': False,
        'allow_initials': True,
        'allow_prefix': True,
        'weight': 2,
    },
    'last': {
        'required': True,
        'allow_initials': True,
        'allow_prefix': False,
        'weight': 5,
    },
}
