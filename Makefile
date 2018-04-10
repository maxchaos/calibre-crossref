PLUGIN = calibre-crossref

SRC_DIR = ./src/calibre-crossref
SOURCES = $(shell find $(SRC_DIR) -iname '*.py')

BUILD_DIR = ./build
## It is important that the tarball has the same basename as the plugin.
TARBALL = $(BUILD_DIR)/$(PLUGIN).zip

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
	calibre-customize --r "$(PLUGIN)" ;

clean:
	[[ -d $(BUILD_DIR) ]] && rm -rf $(BUILD_DIR) ;

run:
	calibre-debug -g
