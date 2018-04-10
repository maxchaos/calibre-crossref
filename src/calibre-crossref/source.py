"""
Metadata retriever for Calibre using Crossref as a source.
"""
import datetime                 # required for processing pubdates

from PyQt5 import QtGui, QtCore
from PyQt5.Qt import *

from calibre.ebooks.metadata.sources.base import Source
from calibre.ebooks.metadata.book.base import Metadata

import calibre.utils.date
from calibre.ebooks.metadata import check_isbn

try:
    from habanero import Crossref as HabaneroBackend
except ImportError:
    pass

class CrossrefSource(Source):
    """Crossref Source."""
    name                    = 'Crossref'
    description             = 'Query crossref.org for metadata'
    action_type             = 'current'
    supported_platforms     = ['linux']
    author                  = 'Panagiotis Vlantis'
    version                 = (0, 0, 2)
    minimum_calibre_version = (0, 8, 0)

    capabilities            = frozenset(['identify'])
    touched_fields          = frozenset(
        ['title', 'authors', 'publisher', 'pubdate', 'series']
    )

    ## If following is True,
    ## then results without ISBN get automatically ignored...
    prefer_results_with_isbn = False

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
        log("Retrieving metadata from Crossref...")
        cands = ()
        getter = HabaneroFrontend()
        ## Perform metadata candidates query.
        cands = getter.query(title, authors, identifiers)
        log("Found {:d} candidates.".format(len(cands)))
        ## Place every metadata candidate in this list.
        for c in cands:
            result_queue.put(c)
        return

class HabaneroFrontend(object):
    """Calibre-Crossref Interface."""
    def __init__(self, logger=None):
        """ TODO """
        ## Logger.
        self._logger = logger
        ## Initialize Crossref backend.
        self._backend = HabaneroBackend()
        ## Initialize plugin parameters to default values.
        self._max_results = 5
        self._timeout = 5       # sec
        self._set_custom_fields = False

    def _log_info(self, msg):
        """Log info-level message."""
        if self._logger:
            self._logger.info(msg)

    def _log_debug(self, msg):
        """Log debug-level message."""
        if self._logger:
            self._logger.debug(msg)

    def _log_error(self, msg):
        """Log error-level message."""
        if self._logger:
            self._logger.error(msg)

    def query(self, title, authors=None, identifiers=None):
        """Query Crossref for all works matching specified criteria."""
        res = self._backend.works(query=title, limit=self._max_results,
                                  timeout=self._timeout)
        status = res["status"]
        if status != "ok":
            msg = "query failed with status {}".format(status)
            self._log_error(msg)
            return ()
        ## Return list of metadata objects.
        ## Each work corresponds to a distinct set of metadata.
        ml = [self._parse_work(work) for work in res["message"]["items"]]
        return ml

    def _parse_work(self, work):
        """Convert work data into calibre metadata."""
        ## Extract title.
        title = work.get("title")[0]
        ## Extract authors.
        authors = []
        for auth in work.get("author", []):
            auth = "{:s} {:s}".format(auth.get("given", ''),
                                      auth.get("family", '')).strip()
            if auth:
                authors.append(auth)
        authors = authors if authors else (u"Unknown",)
        ## Initialize calibre's metadata object (requires title).
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
        if 'isbn' in idents and idents['isbn'] is not None:
            self._log_debug("ISBN: {}".format(idents['isbn']))
            mi.isbn = check_isbn(idents['isbn'])
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
                ## All necessary fields (year, month, day) have been found.
                date = datetime.datetime(*(int(elt) for elt in date_issued))
                return date
        ## Try to infer date from an 'event' field (if present).
        event = work.get('event')
        if event is not None:
            ## Prefer event's starting date over ending date when possible.
            date_event = event.get('start') or event.get('end')
            if date_event is not None:
                date_event = date_event.get('date-parts')[0]
                if len(date_event) == 3:
                    ## All necessary fields (year, month, day) have been found.
                    date = datetime.datetime(*(int(elt) for elt in date_event))
                    return date
        ## Try to infer date from a 'created' field.
        created = work.get('created')
        if created is not None:
            date_created = created.get('date-parts')[0]
            if len(date_created) == 3:
                ## All necessary fields (year, month, day) have been found.
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
