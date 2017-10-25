#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import json

def json_except():
    d = io.StringIO()
    d.write('{"a":b}')
    print(json.loads(d.read()))


def int_except():
    print(int('t'))


if __name__ == "__main__":
    json_except()