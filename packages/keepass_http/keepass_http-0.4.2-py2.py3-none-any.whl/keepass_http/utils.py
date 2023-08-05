# -*- coding: utf-8 -*-
import errno
import logging
import os
import sys

import pkg_resources


def has_gui_support():
    """
    If this fails your Python may not be configured for Tk

    """
    try:
        import Tkinter
    except ImportError:
        return False
    else:
        return True

# http://stackoverflow.com/a/3041990


def query_yes_no(question, default="yes"):  # pragma: no cover
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": "yes", "y": "yes", "ye": "yes",
             "no": "no", "n": "no"}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_absolute_path_to_resource(relative_path):
    return pkg_resources.resource_filename("keepass_http", relative_path)


def is_pytest_running():
    return hasattr(sys, "_pytest_is_running")


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
            raise  # pragma: no cover


def get_logging_filehandlers_streams_to_keep():
    """
    Return all open logging handler file descriptors.
    This is used to avoid closing open file handlers while detaching to background.

    But don't keep /dev/stdout.

    """
    filenos = []
    for handler in logging._handlerList:
        stream = handler().stream
        if stream.name == "<stdout>":
            continue
        filenos.append(stream.fileno())
    return filenos


class Singleton(object):

    """
    Borg pattern

    """
    _we_are_one = {}

    def __new__(cls, *args, **kwargs):
        self = super(Singleton, cls).__new__(cls, *args, **kwargs)
        self.__dict__ = cls._we_are_one
        return self

    def __repr__(self):
        return repr(self.__class__._we_are_one)
