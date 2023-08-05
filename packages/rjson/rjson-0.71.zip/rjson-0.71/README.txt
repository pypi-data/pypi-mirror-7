A simple library for returning N javascript objects from a string

usage:

import rjson

testStr = """
{ "a": "b" } { "a": "c" }
{ "a": "d" }
"""

for result in rjson.parseJson(testStr):
	print result

will return:

{"a": "b"}
{"a": "c"}
{"a": "d"}