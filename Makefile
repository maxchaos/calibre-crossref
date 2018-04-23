SRC_DIR = ./src/calibre_crossref
PLUGIN_METADL_NAME = "Crossref.org"

.PHONY: all install uninstall run

install:
	calibre-customize -b $(SRC_DIR) ;

uninstall:
	calibre-customize -r $(PLUGIN_METADL_NAME) ;

run:
	calibre-debug -g
