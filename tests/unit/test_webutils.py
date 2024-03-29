# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring

import mock
from searx import webutils
from tests import SearxTestCase


class TestWebUtils(SearxTestCase):  # pylint: disable=missing-class-docstring
    def test_prettify_url(self):
        data = (
            ('https://searx.me/', 'https://searx.me/'),
            ('https://searx.me/ű', 'https://searx.me/ű'),
            ('https://searx.me/' + (100 * 'a'), 'https://searx.me/[...]aaaaaaaaaaaaaaaaa'),
            ('https://searx.me/' + (100 * 'ű'), 'https://searx.me/[...]űűűűűűűűűűűűűűűűű'),
        )

        for test_url, expected in data:
            self.assertEqual(webutils.prettify_url(test_url, max_length=32), expected)

    def test_highlight_content(self):
        self.assertEqual(webutils.highlight_content(0, None), None)
        self.assertEqual(webutils.highlight_content(None, None), None)
        self.assertEqual(webutils.highlight_content('', None), None)
        self.assertEqual(webutils.highlight_content(False, None), None)

        contents = ['<html></html>not<']
        for content in contents:
            self.assertEqual(webutils.highlight_content(content, None), content)

        content = 'a'
        query = 'test'
        self.assertEqual(webutils.highlight_content(content, query), 'a')
        query = 'a test'
        self.assertEqual(webutils.highlight_content(content, query), '<span class="highlight">a</span>')

        # pylint: disable=line-too-long
        data = (
            ('" test "', 'a test string', 'a <span class="highlight">test</span> string'),
            ('"a"', 'this is a test string', 'this is <span class="highlight">a</span> test string'),
            (
                'a test',
                'this is a test string that matches entire query',
                'this is <span class="highlight">a</span> <span class="highlight">test</span> string that matches entire query',
            ),
            (
                'this a test',
                'this is a string to test.',
                (
                    '<span class="highlight">this</span> is <span class="highlight">a</span> string to <span class="highlight">test</span>.'
                ),
            ),
            (
                'match this "exact phrase"',
                'this string contains the exact phrase we want to match',
                ''.join(
                    [
                        '<span class="highlight">this</span> string contains the <span class="highlight">exact</span> ',
                        '<span class="highlight">phrase</span> we want to <span class="highlight">match</span>',
                    ]
                ),
            ),
            (
                'a class',
                'a string with class.',
                '<span class="highlight">a</span> string with <span class="highlight">class</span>.',
            ),
        )
        for query, content, expected in data:
            self.assertEqual(webutils.highlight_content(content, query), expected)


class TestUnicodeWriter(SearxTestCase):  # pylint: disable=missing-class-docstring
    def setUp(self):
        self.unicode_writer = webutils.CSVWriter(mock.MagicMock())

    def test_write_row(self):
        row = [1, 2, 3]
        self.assertEqual(self.unicode_writer.writerow(row), None)

    def test_write_rows(self):
        self.unicode_writer.writerow = mock.MagicMock()
        rows = [1, 2, 3]
        self.unicode_writer.writerows(rows)
        self.assertEqual(self.unicode_writer.writerow.call_count, len(rows))


class TestNewHmac(SearxTestCase):  # pylint: disable=missing-class-docstring
    def test_bytes(self):
        data = b'http://example.com'
        with self.assertRaises(AttributeError):
            webutils.new_hmac(b'secret', data)

        with self.assertRaises(AttributeError):
            webutils.new_hmac(1, data)

        res = webutils.new_hmac('secret', data)
        self.assertEqual(res, '23e2baa2404012a5cc8e4a18b4aabf0dde4cb9b56f679ddc0fd6d7c24339d819')
