import requests
from requests.exceptions import ConnectionError

from typing import *
from parlapy.exceptions import NoDocumentsExistException
from . import utils
from .parsers import ParserFactory
from tqdm import tqdm

import time
import json
import os

N_HITS_PER_PAGE = 20
N_MAX_HITS = 10000  # This is a limitation of the ElasticSearch engine
BASE_PARAMS = {'utformat': 'json'}


class API(object):

    def __init__(self, base_url, endpoint_url, content_name, hits_name) -> None:
        super().__init__()

        self.base_url = base_url
        self.endpoint_url = endpoint_url

        self.url = "http://" + \
            "/".join([self.base_url, self.endpoint_url]) + "/"
        self.params = BASE_PARAMS
        self.hits = hits_name
        self.content = content_name

    def filter(self, **params):
        pass

    def query(self, topic):

        self.params.update({
            'sok': topic
        })

    def get(self, params={}):

        # Update with more parameters
        self.params.update(params)

        return self._get_data(self.params)

    def __repr__(self) -> str:
        return self.url

    def _get_data(self, params: Dict):

        limit = params.get('limit', None)
        kind = params.get('kind', None)
        n_hits = 0
        page = 1
        get_more = True

        def allow_more_hits(x, y): return (
            (x < y)) if limit else (x < N_MAX_HITS)

        # Make initial request
        response = self._get_response(params, page)
        content = response.get(self.content)

        # Collect hits
        hits = content.get(self.hits, [])

        n_pages = int(content.get("@sidor", 0))
        page = int(content.get("@sida", 1))

        if page < n_pages:

            progress = tqdm(total=n_pages)
            n_trials = 10

            for page in range(page, n_pages+1):

                # Collect hits on current page
                hits = self._get_hits(params, page, n_trials=n_trials)

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
                    get_more = allow_more_hits(n_hits, limit)

                    if not get_more:
                        break

                    # This should deserialize the response into an appropriate object
                    yield parser.parse(hit)

                progress.update(1)

    def _get_hits(self, params, page, n_trials=10):

        while True:

            n_trials -= 1
            try:

                # Make request
                response = self._get_response(params, page)
                content = response.get(self.content)

                # Collect hits
                return content.get(self.hits, [])

            except ConnectionError as err:
                if n_trials == 0:
                    raise err
                else:
                    time.sleep(1)

    def _get_response(self, params: Dict, page: int):

        # Perform the HTTP request, using page=page
        params['p'] = page

        response = requests.get(self.url, params=params)

        return response.json()

    def collect(self):
        return [x for x in self.get()]


class Documents(API):

    config_path = 'configs/search.json'

    filename = os.path.join(os.path.dirname(__file__), config_path)

    with open(filename, 'r') as f:
        param_map = json.load(f)

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

    def get(self, params={}):
        yield from super().get(params)
