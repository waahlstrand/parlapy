import requests
import copy
import json
from typing import List, Dict, Optional
from functools import lru_cache

apis = {
    'persons': 'personlista',
    'documents': 'dokumentlista',
    'votes': 'voteringlista' 
}

n_hits_per_page = 20

def filter_method(obj, param):

    def method(query):

        obj.params.update({obj.param_map[param]: query})

        return obj

    return method

class API(object):

    def __init__(self, base_url, endpoint_url) -> None:
        super().__init__()

        self.url = "/".join([base_url, endpoint_url])
        self.params = dict()
        self.hits = ""
        self.content = ""

    def filter(self, **params):
        pass

    def query(self, topic):
        pass

    def get(self):
        
        return self._get_response(self.params)

    def __repr__(self) -> str:
        return self.url


    def _get_data(self, params: Dict, limit: int):

        n_hits = 0
        page = 1
        has_more = True
        while has_more:

            # Make call to API
            response = self._get_response(params, page)

            # Parse content
            content = response.get(self.content)
            hits = content.get(self.hits)

            # Check if there is a next page
            has_next_page = self.next_page in content.keys()
            
            for hit in hits:

                # Parse item type
                
                yield hit

            # Increase counters towards limit and test yield
            page += 1
            n_hits += len(hits)
            has_more = (n_hits < limit) and has_next_page


    @lru_cache(maxsize=n_hits_per_page)
    def _get_response(self, params: Dict, page: int):

        # Perform the HTTP request, using page=page
        params['p'] = page

        response = requests.get(self.api, params=params)

        return response.json()
    
class Riksdag(object):

    base_url: str = 'data.riksdagen.se'

    def __init__(self):
        super().__init__()

    def filter(self):
        pass

    def to_pandas(self):
        pass

class Persons(API):

    def __init__(self, base_url, endpoint_url) -> None:
        super().__init__(base_url, endpoint_url)

class Documents(API):

    param_map = {
        'query': 'sok', 
        'type': 'doktyp', 
        'rm': 'rm', 
        'from': 'from',
        'to':'tom', 
        'ts':'ts', 
        'bet':'bet', 
        'tempbet':'tempbet',
        'nr':'nr',
        'org':'org', 
        'iid':'iid',
        'avd':'avd',
        'webbtv': 'webbtv',
        'speaker': 'talare', 
        'exakt':'exakt',
        'planering':'planering', 
        'facets':'facets',
        'sort':'sort', 
        'rel':'rel',
        'sortorder': 'sortorder',
        'rapport': 'rapport'
    }

    parameters = param_map.values()
    filters = param_map.keys()

    def __init__(self, base_url, endpoint_url) -> None:
        super().__init__(base_url, endpoint_url)

        for name, param in Documents.param_map.items():
            setattr(self, name, filter_method(self, name))
            self.params.update({param: ''})


    def between(self, start, end):
        """Filters the results between a start and end date. Equivalent to
        >> documents.from(start).to(end)

        Args:
            start (str): Start date in ISO- format
            end (str): End date in ISO- format

        Returns:
            Documents: The Documents API instance
        """

        self.params.update({
            'from': start,
            'tom': end
            })

        return self

    def motions(self, query):
        """Filters the results by motions matching a free text query. Equivalent to
        >> documents.type('motion').query(query)

        Args:
            query (str): A free form text query

        Returns:
            Documents: The Documents API instance
        """

        self.params.update({
            'doktyp': 'mot',
            'sok': query
        })

        return self

    def sort(self, by, order):

        self.params.update({
            'sort': by,
            'sortorder': order
        })

        return self


class Votes(API):

    def __init__(self, base_url, endpoint_url) -> None:
        super().__init__(base_url, endpoint_url)


# Add APIs to the Riksdag class
for (attr, endpoint), api in zip(apis.items(), [Persons, Documents, Votes]):

    setattr(Riksdag, attr, api(Riksdag.base_url, endpoint))