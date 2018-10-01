# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import inspect
import logging
import sys

from os.path import isfile

from mycroft.util.json_helper import load_commented_json


def getLogger(name="MYCROFT"):
    """Depreciated. Use LOG instead"""
    return logging.getLogger(name)


def _make_log_method(fn):
    @classmethod
    def method(cls, *args, **kwargs):
        cls._log(fn, *args, **kwargs)

    method.__func__.__doc__ = fn.__doc__
    return method


class LOG:
    """
    Custom logger class that acts like logging.Logger
    The logger name is automatically generated by the module of the caller

    Usage:
        >>> LOG.debug('My message: %s', debug_str)
        13:12:43.673 - :<module>:1 - DEBUG - My message: hi
        >>> LOG('custom_name').debug('Another message')
        13:13:10.462 - custom_name - DEBUG - Another message
    """

    _custom_name = None
    handler = None
    level = None

    # Copy actual logging methods from logging.Logger
    # Usage: LOG.debug(message)
    debug = _make_log_method(logging.Logger.debug)
    info = _make_log_method(logging.Logger.info)
    warning = _make_log_method(logging.Logger.warning)
    error = _make_log_method(logging.Logger.error)
    exception = _make_log_method(logging.Logger.exception)

    @classmethod
    def init(cls):
        sys_config = '/etc/mycroft/mycroft.conf'
        config = load_commented_json(sys_config) if isfile(sys_config) else {}
        cls.level = logging.getLevelName(config.get('log_level', 'DEBUG'))
        fmt = '%(asctime)s.%(msecs)03d - ' \
              '%(name)s - %(levelname)s - %(message)s'
        datefmt = '%H:%M:%S'
        formatter = logging.Formatter(fmt, datefmt)
        cls.handler = logging.StreamHandler(sys.stdout)
        cls.handler.setFormatter(formatter)
        cls.create_logger('')  # Enables logging in external modules

    @classmethod
    def create_logger(cls, name):
        l = logging.getLogger(name)
        l.propagate = False
        l.addHandler(cls.handler)
        l.setLevel(cls.level)
        return l

    def __init__(self, name):
        LOG._custom_name = name

    @classmethod
    def _log(cls, func, *args, **kwargs):
        if cls._custom_name is not None:
            name = cls._custom_name
            cls._custom_name = None
        else:
            # Stack:
            # [0] - _log()
            # [1] - debug(), info(), warning(), or error()
            # [2] - caller
            stack = inspect.stack()

            # Record:
            # [0] - frame object
            # [1] - filename
            # [2] - line number
            # [3] - function
            # ...
            record = stack[2]
            mod = inspect.getmodule(record[0])
            module_name = mod.__name__ if mod else ''
            name = module_name + ':' + record[3] + ':' + str(record[2])
        func(cls.create_logger(name), *args, **kwargs)

LOG.init()
