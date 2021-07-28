import requests
import copy
import json
from typing import *
from functools import lru_cache
from . import utils
from .parsers import ParserFactory

N_HITS_PER_PAGE = 20
N_MAX_HITS = 10000 # This is a limitation of the ElasticSearch engine
BASE_PARAMS = {'utformat': 'json'}

class API(object):

    def __init__(self, base_url, endpoint_url, content_name, hits_name) -> None:
        super().__init__()

        self.base_url = base_url
        self.endpoint_url = endpoint_url

        self.url = "http://" + "/".join([self.base_url, self.endpoint_url]) + "/"
        self.params = BASE_PARAMS
        self.hits = hits_name
        self.content = content_name

    def filter(self, **params):
        pass

    def query(self, topic):

        self.params.update({
            'sok': topic
        })

    def get(self, params = {}):
        
        # Update with more parameters
        self.params.update(params)
        
        return self._get_data(self.params)

    def __repr__(self) -> str:
        return self.url

    def _get_data(self, params: Dict):

        limit = params.get('limit', None)
        kind  = params.get('kind', None)

        allow_more_hits = lambda x, y: ((x < y)) if limit else (x < N_MAX_HITS)

        n_hits = 0
        page = 1
        has_more = True
        while has_more:

            # Make call to API
            response = self._get_response(params, page)

            # Parse content
            content = response.get(self.content)
            hits = content.get(self.hits)

            # If we have a set document kind, we only need one parser
            if kind is not None:
                parser = ParserFactory.create(kind)
            
            # TODO: Split into proper generator class
            for hit in hits:
                
                # If we do not have a set document kind, 
                # check each document and parse separately
                if kind is None:
                    hit_kind = hit.get('doktyp', None) or 'base'
                    parser = ParserFactory.create(hit_kind)
                
                # Check if we have hit the limit
                has_more = allow_more_hits(n_hits, limit)

                if not has_more:
                    break
                
                # This should deserialize the response into an appropriate object
                yield parser.parse(hit)

                # Increase n_hits
                n_hits += 1

            # Increase counters towards limit and test yield
            page += 1

    def _get_response(self, params: Dict, page: int):

        # Perform the HTTP request, using page=page
        params['p'] = page

        response = requests.get(self.url, params=params)

        return response.json()

    def collect(self):
        return [x for x in self.get()]


class Documents(API):

    param_map = {
        'query': 'sok', 
        'kind': 'doktyp', 
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

    def __init__(self) -> None:

        base_url = 'data.riksdagen.se'
        endpoint_url = 'dokumentlista'
        hits_name = 'dokument'
        content_name = 'dokumentlista'

        super().__init__(base_url, 
                        endpoint_url, 
                        content_name, 
                        hits_name)

        for name, param in Documents.param_map.items():
            setattr(self, name, utils.filter_method(self, name))
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

    def kind(self, kind): 

        self.params.update({
            'doktyp': kind
            })

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

    def limit(self, limit):

        self.params.update({
            'limit': limit
        })

        return self

    def get(self, params = {}):
        yield from super().get(params)