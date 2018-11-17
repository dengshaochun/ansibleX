#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 14:03
# @Author  : Dengsc
# @Site    : 
# @File    : validators.py
# @Software: PyCharm

import re
import yaml
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


def validate_dict_format(value):
    """
    validate string is python dict format
    :param value: <str>
    :return: None
    """
    try:
        dict(yaml.safe_load(value))
    except Exception:
        raise ValidationError(
            _('%(value)s is not an python dict decode string.'),
            params={'value': value},
        )


def convert_json_to_dict(value):
    """
    convert json data to python dict
    :param value: <str> value
    :return: <dict> value
    """
    return dict(yaml.safe_load(value))


def validate_unit(value):
    """
    validate string unit
    :param value: <str>
    :return: 
    """

    try:
        size = str(value)
        if size == 'max':
            return True
        _pat = r'([\d.]+)([KMGTP]?)$'
        result = re.compile(_pat).match(size).groups()
        if result:
            return True
        else:
            raise ValidationError(
                _('%(value)s is not unit format.'),
                params={'value': value},
            )
    except Exception:
        raise ValidationError(
            _('%(value)s is not unit format.'),
            params={'value': value},
        )
