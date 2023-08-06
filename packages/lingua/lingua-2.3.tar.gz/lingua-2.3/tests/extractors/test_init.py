from lingua.extractors import check_c_format
from lingua.extractors import Keyword


def test_basic_c_format():
    flags = []
    check_c_format('Hello, %s', flags)
    assert 'c-format' in flags


def test_accept_no_format_hint():
    flags = ['no-c-format']
    check_c_format('Hello, %s', flags)
    assert 'c-format' not in flags


def test_escaped_percent_sign():
    flags = []
    check_c_format('100%%', flags)
    assert 'c-format' not in flags


def test_strftime_is_not_c_format():
    flags = []
    check_c_format('%Y-%m-%d', flags)
    assert 'c-format' not in flags


class TestKeywordFromSpec(object):
    def test_minimal(self):
        kw = Keyword.from_spec('gettext')
        assert kw.function == 'gettext'
        assert kw.msgid_param == 1
        assert kw.msgid_plural_param is None

    def test_custom_msgid_param(self):
        kw = Keyword.from_spec('i18n_log:2')
        assert kw.function == 'i18n_log'
        assert kw.msgid_param == 2
        assert kw.msgid_plural_param is None

    def test_plural(self):
        kw = Keyword.from_spec('ngettext:1,2')
        assert kw.function == 'ngettext'
        assert kw.msgid_param == 1
        assert kw.msgid_plural_param == 2

    def test_domain_param(self):
        kw = Keyword.from_spec('dgettext:1d,2')
        assert kw.function == 'dgettext'
        assert kw.msgid_param == 2
        assert kw.msgid_plural_param is None
        assert kw.domain_param == 1

    def test_parameter_count(self):
        kw = Keyword.from_spec('myfunc:1,5t')
        assert kw.function == 'myfunc'
        assert kw.msgid_param == 1
        assert kw.msgid_plural_param is None
        assert kw.required_arguments == 5
