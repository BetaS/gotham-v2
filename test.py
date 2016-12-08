#encoding: utf-8

import bson

origin = {'a': 1}
print origin

data = bson.dumps(origin)
print data

data = bson.loads(data)
print data['a']