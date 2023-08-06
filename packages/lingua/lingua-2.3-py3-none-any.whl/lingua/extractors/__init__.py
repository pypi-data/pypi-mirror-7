from __future__ import print_function
import collections
import os
import re
import sys


Message = collections.namedtuple('Message',
        'msgctxt msgid msgid_plural flags comment tcomment location')

EXTRACTORS = {}
EXTENSIONS = {}


def register_extractor(identifier, extensions):
    def wrapper(func):
        EXTRACTORS[identifier] = func
        for extension in extensions:
            EXTENSIONS[extension] = func
        return func
    return wrapper


def get_extractor(filename):
    ext = os.path.splitext(filename)[1]
    return EXTENSIONS.get(ext)


# Based on http://www.cplusplus.com/reference/cstdio/printf/
_C_FORMAT = re.compile(r'''
        %
        [+ #0-]?              # flags
        (\d+|\*)?             # width
        (\.(\d+|\*))?         # precision
        (hh?|ll?|j|z|t|L)?    # length
        [diuoxXfFeEgGaAcspn%] # specifier
        ''', re.VERBOSE)


def check_c_format(buf, flags):
    if 'no-c-format' in flags:
        return
    if all(_C_FORMAT.match(buf[m.start():]) is not None
            for m in re.finditer('%(?!%)', buf)):
        flags.append('c-format')
    return


# Based on http://docs.python.org/2/library/string.html#format-string-syntax
_PYTHON_FORMAT = re.compile(r'''
        \{
            (([_A-Za-z](\w*)(\.[_a-z]\w*|\[\d+\])?)|\w+)?  # fieldname
            (![rs])?  # conversion
            (:\.?[<>=^]?[+ -]?\w*,?(\.\w+)?[bcdeEfFgGnosxX%]?)?  # format_spec
        \}
        ''', re.VERBOSE)


def check_python_format(buf, flags):
    if 'no-python-format' in flags:
        return
    if _PYTHON_FORMAT.search(buf) is not None:
        flags.append('python-format')


class Keyword(object):
    msgctxt_param = None
    domain_param = None
    comment = u''
    required_arguments = None

    _comment_arg = re.compile(r'^"(.*)"$')

    def __init__(self, function, msgid_param=1, msgid_plural_param=None, domain_param=None):
        self.function = function
        self.msgid_param = msgid_param
        self.msgid_plural_param = msgid_plural_param
        self.domain_param = domain_param

    @classmethod
    def from_spec(cls, spec):
        if ':' not in spec:
            return cls(spec)
        try:
            (function, args) = spec.split(':', 1)
            kw = cls(function)
            seen_msgid_param = False
            while args:
                if cls._comment_arg.match(args) is not None:
                    kw.comment = args[1:-1]
                    break
                (param, args) = args.split(',', 1) if ',' in args else (args, '')
                if param.endswith('c'):
                    kw.msgctxt_param = int(param[:-1])
                elif param.endswith('d'):
                    kw.domain_param = int(param[:-1])
                elif param.endswith('t'):
                    kw.required_arguments = int(param[:-1])
                elif not seen_msgid_param:
                    kw.msgid_param = int(param)
                    seen_msgid_param = True
                else:
                    kw.msgid_plural_param = int(param)
        except SyntaxError:
            raise ValueError('Invalid keyword spec: %s' % spec)
        return kw


def update_keywords(keywords, specs):
    for spec in specs:
        if not spec:
            keywords.clear()
        try:
            kw = Keyword.from_spec(spec)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        keywords[kw.function] = kw
