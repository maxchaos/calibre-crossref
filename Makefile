SRC_DIR = ./src/calibre-crossref
SOURCES = $(shell find $(SRC_DIR) -iname '*.py')

BUILD_DIR = ./build
TARBALL = $(BUILD_DIR)/calibre-crossref.zip

.PHONY: all install uninstall clean run

$(TARBALL): $(SOURCES) | $(BUILD_DIR)
	tmpdir=$$(mktemp -d -p /tmp calibre-crossref-XXXXX) ; \
	tmpfile=$${tmpdir}/tarball.zip ; \
	[[ -d $${tmpdir} ]] && \
	( cd "$(SRC_DIR)" && zip -r $${tmpfile} * ) && \
	cp $${tmpfile} $(TARBALL) ;

$(BUILD_DIR):
	mkdir -p $@ ;

install: $(TARBALL)
	calibre-customize --a "$(TARBALL)" ;

uninstall:
	calibre-customize --r "Crossref" ; # Name of the plugin.

clean:
	[[ -d $(BUILD_DIR) ]] && rm -rf $(BUILD_DIR) ;

run:
	calibre-debug -g
