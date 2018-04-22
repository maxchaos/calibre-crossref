import datetime                 # required for processing pubdates

from calibre.ebooks.metadata.book.base import Metadata
import calibre.utils.date
from calibre.ebooks.metadata import check_isbn

try:
    from habanero import Crossref
except ImportError:
    pass

class HabaneroBackend(object):
    """Calibre-Crossref Interface via habanero."""
    def __init__(self, logger=None):
        """ TODO """
        ## Logger.
        self._logger = logger
        ## Initialize Crossref backend.
        try:
            self._crossref = Crossref()
        except NameError:
            msg = "could not load habanero backend"
            self._log_error(msg)
            raise RuntimeError(msg)
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
        res = self._crossref.works(query=title, limit=self._max_results,
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
        self._log_debug("")
        ## Extract title.
        title = work.get("title")[0]
        title = title if title is not None else u"Unknown"
        self._log_debug("Title: '{}'".format(title))
        ## Extract authors.
        authors = []
        for auth in work.get("author", []):
            auth = "{:s} {:s}".format(auth.get("given", ''),
                                      auth.get("family", '')).strip()
            if auth:
                authors.append(auth)
        authors = authors if authors else (u"Unknown",)
        self._log_debug("Authors: {}".format(repr(authors)))
        ## Initialize calibre's metadata object (requires title).
        mi = Metadata(title, authors)
        ## Extract identifiers.
        self._log_debug("Identifiers:")
        idents = {
            'isbn': work.get('ISBN'),
            'doi': work.get('DOI'),
            'issn': work.get('ISSN')
        }
        for k, v in idents.items():
            if v is not None and isinstance(v, (list, tuple)):
                idents[k] = v[0]
        for k, v in idents.items():
            if v is not None and k != 'isbn':
                mi.set_identifier(k, v)
                self._log_debug("\t {}: {}".format(k, v))
        if 'isbn' in idents and idents['isbn'] is not None:
            mi.isbn = check_isbn(idents['isbn'])
            self._log_debug("\t isbn: {}".format(idents['isbn']))
        ## Extract published date.
        pubdate = self._parse_work_pubdate(work)
        if pubdate is not None:
            pubdate = pubdate.replace(tzinfo=calibre.utils.date.utc_tz)
        mi.pubdate = pubdate
        self._log_debug("Pubdate: {}".format(repr(pubdate)))
        ## Extract publisher.
        publisher = self._parse_work_publisher(work)
        self.publisher = publisher
        self._log_debug("Publisher: {}".format(publisher))
        ## Return extracted data.
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
        ## Try to infer date from a 'published-print' field.
        published_print = work.get('published-print')
        if published_print is not None:
            date_published_print = published_print.get('date-parts')[0]
            if len(date_published_print) == 3:
                ## All necessary fields (year, month, day) have been found.
                date = datetime.datetime(
                    *(int(elt) for elt in date_published_print))
                return date
        ## TODO: try to infer missing date parameters from multiple fields
        ## If everything failed, return nothing.
        return None

    def _parse_work_publisher(self, work):
        """ TODO """
        return work.get('publisher', None)
