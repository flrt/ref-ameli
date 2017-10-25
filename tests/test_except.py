#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import json
import unittest


class TestRegex(unittest.TestCase):
    def test_json_except(self):
        with self.assertRaises(json.decoder.JSONDecodeError) as context:
            d = io.StringIO()
            d.write('{"a":b}')
            print(json.loads(d.read()))

            self.assertTrue('Expecting value: ' in str(context.exception))

    def test_int_except(self):
        with self.assertRaises(ValueError) as context:
            print(int('t'))
            self.assertTrue('invalid literal for int()' in str(context.exception))


if __name__ == '__main__':
    unittest.main()
