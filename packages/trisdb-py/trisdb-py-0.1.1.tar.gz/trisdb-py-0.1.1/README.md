trisdb-py
=========

The Python interface to TrisDb

### Installation
```
sudo pip install trisdb-py
```

### Usage
```python
>>> from trisdb import *

>>> db = TrisDbConnection('localhost', 1205)
>>> db.create('Alice', 'loves', 'pizza')
>>> db.create('Kate', 'likes', 'football')

>>> # Print all records
>>> result = db.get('*')
>>> for i in result:
>>>    print i['subject'] + '-' + i['predicate'] + '-' + i['object']

>>> # Who likes football?
>>> result = db.gets('*', 'likes', 'football')
>>> for i in result:
>>>    print i

>>> db.clear()
```
