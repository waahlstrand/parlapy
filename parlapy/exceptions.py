class ParlapyException(Exception):
    """The base exception that all other exceptions extend
    """

class DocumentDoesNotExistException(ParlapyException):

    def __init__(self, url) -> None:
        super().__init__(f"""
            The document at the url {url} does not seem to exist.
        """)

class ParserAlreadyExistsException(ParlapyException):
    def __init__(self, url) -> None:
        super().__init__(f"""
            The parser already exists.
        """)