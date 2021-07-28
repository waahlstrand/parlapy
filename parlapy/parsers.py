import json
from typing import *
from .models import Person, Motion, Document
from .exceptions import *

import datetime

class Parser:
    """The parser builds objects from dict responses
    """

class ParserFactory:
    """The parser factory generates parsers for Parlapy objects depending on their document kind
    """
    parsers = {}

    @classmethod
    def register(cls, key: str):

        def inner(wrapped_class: Parser) -> Callable:
            if key in cls.parsers:
                raise ParserAlreadyExistsException
            cls.parsers[key] = wrapped_class

            return wrapped_class

        return inner

    @classmethod
    def create(cls, key: str, **kwargs) -> Parser:
        parser = cls.parsers.get(key)
        if not parser:
            raise ValueError(key)
        return parser(**kwargs)


@ParserFactory.register('base')
class DocumentParser(Parser):
    """Base parser for all documents. Simply makes attributes accessible by name
    """

    def parse(self, response: Dict) -> Document:

        d = Document()
        d.__dict__ = response
        
        return d

@ParserFactory.register('person')
class PersonParser:
    
    def parse(self, response: Dict) -> Person:

        id      = response.get('intressent_id', None)
        name    = response.get('namn', None)
        party   = response.get('partibet', None)

        return Person(id=id, name=name, party=party)


@ParserFactory.register('mot')
class MotionParser(Parser):

    def parse(self, response: Dict) -> Motion:
        
        date_str            = response.get('datum', None)
        id                  = response.get('id', None)
        title               = response.get('titel', None)
        subtitle            = response.get('undertitel', None)
        doc_id              = response.get('dok_id', None)
        author_list         = response.get('dokintressent', []) 
        document_url_text   = response.get('dokument_url_text', None)

        # Parse the date to a datetime object
        date = self._parse_date(date_str)

        # Parse the document url
        document_url = self._parse_document_url(document_url_text)

        # Parse the author list
        authors = self._parse_persons(author_list)

        return Motion(id, doc_id, date, title, subtitle, document_url, authors)


    def _parse_document_url(self, url: str) -> str:
        try:
            return url.replace('.text', '')
        except AttributeError: 
            raise DocumentDoesNotExistException(url)

    def _parse_persons(self, person_list: List[Dict]) -> List[Person]:
        # TODO: Not done

        parser = ParserFactory.create('person')

        if person_list:

            author_params = person_list.get('intressent', [])
            authors = [parser.parse(a) for a in author_params]
        
        else:
            authors = []

        return authors

    def _parse_date(self, date: str) -> datetime.datetime:
        try:
            return datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")

