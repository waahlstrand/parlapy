import requests
from typing import *
from .exceptions import *
import datetime

class Riksdagsdata:
    """Common base class for all objects at Riksdagsdata. Implements hash ids.
    """

    def __init__(self, id: str) -> None:
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

class Document(Riksdagsdata):
    """Common base class for all document objects at Riksdagsdata
    """

class Person(Riksdagsdata):
    def __init__(self, id: str, name: str, party: str) -> None:

        super().__init__(id)

        self.name = name
        self.party = party

    def __str__(self):
        return f'{self.name} ({self.party})'

    def __repr__(self):
        return str(self)

def get_document(url: str, **params: Optional[Dict]):

    if url is not None:
        try:
            response = requests.get(url, **params)
            return response
        except requests.exceptions.RequestException:
            raise DocumentDoesNotExistException(url)
    else:
        raise DocumentDoesNotExistException(url) 


class Motion(Document):

    def __init__(self, id: str, 
                       doc_id: str, 
                       date: datetime.datetime, 
                       title: str,
                       subtitle: str,
                       document_url: str,
                       authors: List[Person]) -> None:
        
        super().__init__(id)

        self.doc_id = doc_id
        self.date = date
        self.title = title
        self.subtitle = subtitle
        self.authors = authors
        self.document_url = document_url

        self.text = None
        self.html = None

    def to_text(self, **params: Optional[Dict]) -> str:
        # TODO: Does not actually return text, but rather XML...
        
        text_url = "https:" + self.document_url + ".text"
        if self.text is None:
            self.text = get_document(text_url, **params)

        return self.text

    def to_html(self, **params: Optional[Dict]) -> str:

        html_url = "https:" + self.document_url + ".html"
        if self.html is None:
            self.html = get_document(html_url, **params)

        return self.html.text


    def __str__(self) -> str:
        return f'Motion: {self.title}'

    def __repr__(self) -> str:
        return str(self)
        

