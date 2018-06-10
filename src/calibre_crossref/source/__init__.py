"""
Metadata Downloader for Calibre using Crossref.
"""
from calibre.ebooks.metadata.sources.base import Source

from .habanero_backend import HabaneroBackend

class CrossrefSource(Source):
    """Crossref Source.

    Front-end class for retrieving scientific article metadata from Crossref.
    It uses a back-end to download the metadata, which then passes back to
    Calibre.

    """
    name                    = 'Crossref.org'
    description             = 'Download document metadata from crossref.org.'
    action_type             = 'current'
    supported_platforms     = ['linux']
    author                  = 'Panagiotis Vlantis'
    version                 = (0, 0, 6)
    minimum_calibre_version = (0, 8, 0)

    capabilities            = frozenset(['identify'])
    touched_fields          = frozenset(
        ['title', 'authors', 'publisher', 'pubdate']
    )

    ## If following is True,
    ## then results without ISBN get automatically ignored...
    ## In general, we don't want that.
    prefer_results_with_isbn = False

    def identify(self,
                 log, result_queue, abort,
                 title=None, authors=None, identifiers=None,
                 timeout=30):
        """ TODO """
        cands = ()
        ## Currently, only one back-end is implemented.
        getter = HabaneroBackend(logger=log)
        log("Retrieving metadata from Crossref...")
        cands = getter.query(title, authors, identifiers)
        log("Found {:d} candidates.".format(len(cands)))
        ## Place every metadata candidate in this list.
        for c in cands:
            result_queue.put(c)
        return
