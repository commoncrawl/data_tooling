"""
Define the base classes for Pii Tasks
"""

import regex
from typing import Iterable, Callable

from ..piientity import PiiEntity
from .exception import PiiUnimplemented


class BasePiiTask:
    """
    Base class for a Pii Task
    """

    def __init__(self, **kwargs):
        self.pii = kwargs.pop("pii")
        self.lang = kwargs.pop("lang")
        self.country = kwargs.pop("country", None)
        self.doc = kwargs.pop("doc", None)
        self.options = kwargs

    def find(self, doc: str) -> Iterable[PiiEntity]:
        raise PiiUnimplemented("missing implementation for Pii Task")

    def __call__(self, doc: str) -> Iterable[PiiEntity]:
        return self.find(doc)


class RegexPiiTask(BasePiiTask):
    """
    A wrapper for a PII implemented as a regex pattern
    Instead of the standard re package it uses the regex package (in
    backwards-compatible mode)
    """

    def __init__(self, pattern: str, doc: str, **kwargs):
        super().__init__(**kwargs)
        self.regex = regex.compile(pattern, flags=regex.X | regex.VERSION0)
        self.doc = doc

    def find(self, doc: str) -> Iterable[str]:
        for cc in self.regex.finditer(doc):
            yield PiiEntity(self.pii, cc.start(), cc.group(), country=self.country)


class CallablePiiTask(BasePiiTask):
    """
    A wrapper for a PII implemented as a function
    """

    def __init__(self, call: Callable, **kwargs):
        super().__init__(**kwargs)
        self.call = call
        self.doc = call.__doc__ or self.pii.name

    def find(self, doc: str) -> Iterable[PiiEntity]:
        for cc in self.call(doc):
            start = 0
            while True:
                pos = doc.find(cc, start)
                if pos < 0:
                    break
                yield PiiEntity(self.pii, pos, cc, country=self.country)
                start = pos + len(cc)
