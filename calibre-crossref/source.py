
import datetime                 # required for processing pubdates

from PyQt5 import QtGui, QtCore
from PyQt5.Qt import *

from calibre.ebooks.metadata.sources.base import Source
from calibre.ebooks.metadata.book.base import Metadata

import calibre.utils.date
from calibre.ebooks.metadata import check_isbn

from habanero import Crossref

class CrossrefSource(Source):
    """Class interfacing crossref retriever inside calibre."""
    name                    = 'Crossref'
    description             = 'Query crossref.org for metadata'
    action_type             = 'current'
    # supported_platforms     = ['windows', 'osx', 'linux']
    supported_platforms     = ['linux']
    author                  = 'Panagiotis Vlantis'
    version                 = (0, 0, 1)
    minimum_calibre_version = (0, 8, 0)

    capabilities            = frozenset(['identify'])
    touched_fields          = frozenset(
        ['title', 'authors', 'publisher', 'pubdate', 'series']
    )

    def config_widget(self):
        """ TODO """
        pass

    def save_setting(self, config_widget):
        """ TODO """
        pass

    def identify(self,
                 log, result_queue, abort,
                 title=None, authors=None, identifiers=None,
                 timeout=30):
        """ TODO """

        getter = CrossrefAPI()
        if title:
            cands = getter.query_title(title, authors)
        for c in cands:
            result_queue.put(c)
        log("foobar")

        ## Retrieve metadata here.
        # msg = "NOT IMPLEMENTED"
        # raise NotImplementedError(msg)

        ## Place every metadata candidate in this list
        # result_queue.append()
        return

class CrossrefAPI(object):
    """Interface for Crossref database."""
    _api = Crossref()
    def __init__(self):
        """ TODO """
        self._max_results = 100

    def query_title(self, title, authors=None):
        """Query crossref for all works with specified title.

        Optional argument AUTHORS can be used for filtering results."""
        res = self._api.works(query=title, limit=self._max_results)
        status = res["status"]
        if status != "ok":
            msg = "query failed with status {}".format(status)
            raise RuntimeError(msg)
        ## Construct list of metadata objects.
        ## Each work corresponds to a distinct set of metadata.
        ml = [self._parse_work(work) for work in res["message"]["items"]]

        return ml

    def _parse_work(self, work):
        """Convert work data into calibre metadata."""
        title = work.get("title")[0]
        authors = []
        for auth in work.get("author", []):
            authors.append("{:s} {:s}".format(
                auth.get("given", ''), auth.get("family", '')
            ))
        authors = authors if authors else (u"Unknown",)
        ## Initialize calibre's metadata object (requires title)
        mi = Metadata(title, authors)
        ## Extract identifiers.
        idents = {
            'isbn': work.get('ISBN'),
            'doi': work.get('DOI'),
            'issn': work.get('ISSN')
        }
        for k, v in idents.items():
            if v is not None and isinstance(v, (list, tuple)):
                idents[k] = v[0]
        for k, v in idents.items():
            if v is not None and k is not 'isbn':
                mi.set_identifier(k, v)
        ## TODO: Fix isbn related error
        # print "ISBN: ", idents['isbn']
        # if 'isbn' in idents and idents['isbn'] is not None:
        #     mi.isbn = check_isbn(idents['isbn'])

        # mi.set_identifier('identifiers', idents)
        # if 'isbn' in idents:
        #     mi.set_identifier('isbn', idents['isbn'])
        ## Extract published date.
        mi.set_identifier('pubdate',
                          self._parse_work_pubdate(work).date().isoformat())
        return mi

    def _parse_work_pubdate(self, work):
        """Infer publish date information."""
        ## If issued date is complete, use that.
        issued = work.get('issued')
        if issued is not None:
            date_issued = issued.get('date-parts')[0]
            if len(date_issued) == 3:
                ## All necessary fields (year, month and day) have been found
                date = datetime.datetime(*(int(elt) for elt in date_issued))
                return date
        ## Try to infer date from an 'event' field (if present).
        event = work.get('event')
        if event is not None:
            ## Prefer event's starting date over ending date if possible.
            date_event = event.get('start') or event.get('end')
            if date_event is not None:
                date_event = date_event.get('date-parts')[0]
                if len(date_event) == 3:
                    ## All necessary fields (year, month and day) have been found
                    date = datetime.datetime(*(int(elt) for elt in date_event))
                    return date
        ## Try to infer date from a 'created' field.
        created = work.get('created')
        if created is not None:
            date_created = created.get('date-parts')[0]
            if len(date_created) == 3:
                ## All necessary fields (year, month and day) have been found
                date = datetime.datetime(*(int(elt) for elt in date_created))
                return date
        ## TODO: attempt to extract dates from fields 'published-print'.
        ## TODO: try to infer missing date parameters from multiple fields
        ## If everything failed, return nothing.
        return None

    def _parse_work_publisher(self):
        """ TODO """
        msg = "NOT IMPLEMENTED"
        raise NotImplementedError(msg)

class ConfigWidget(QWidget):
    """Plugin's Configuration Widget."""
    pass

