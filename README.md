# parlapy ☂️
A convenient Python wrapper for the public API of the Swedish Parliament data.

## Features
The API wrapper is still in progress, but will initially support
- Querying the public *documents* endpoint (``data.riksdagen.se/dokumentlista``) for a number of different kinds of documents.
- Parsing the document responses into objects with named attributes.
- Special support for *motions* and their author members of parliament.
  - Listing all authors of a motion
  - Normalization and checks for parties
  - Fetching ("scraping") the html motions

### Future features
Future support will include querying the *votes* and *persons* endpoints (``data.riksdagen.se/voteringslista``, ``data.riksdagen.se/personlista``), as well as integration with pandas.

## Usage
The wrapper supports a simplified API for specifying queries, limiting the response and filtering the document type.

```python
from parlapy.api import Documents

documents = Documents()

ds = documents.motions('arbetsmarknad')\
              .limit(33)\
              .between('2020-01-01', '2021-12-21') 
```

The queries are lazy, and either fetch them manually,
```python

motions = [d for d in ds.get()]

```
or collect them immediately.
```
motions = documents.query('arbetsmarknad')\
                   .kind('mot')\
                   .limit(33)\
                   .between('2020-01-01', '2021-12-21')\
                   .collect()
```


