
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import *

from calibre.ebooks.metadata.sources.base import Source
from calibre.ebooks.metadata.book.base import Metadata

from habanero import Crossref

class MetadataRetriever(Source):
    """Class interfacing crossref retriever inside calibre."""
    name                    = 'Citation Getter'
    description             = 'Query crossref for metadata'
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
        """ """
        pass

    def save_setting(self, config_widget):
        """ """
        pass

    def identify(self,
                 log, result_queue, abort,
                 title=None, authors=None, identifiers={}, 
                 timeout=30):

        getter = Crossref()
        if title:
            getter.works(query=title)
        
        ## Retrieve metadata here.
        msg = "NOT IMPLEMENTED"
        raise NotImplementedError(msg)

        ## Place every metadata candidate in this list
        result_queue.append()
        return

class ConfigWidget(QWidget):
    """Plugin's Configuration Widget."""
    pass
    
