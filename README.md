
# calibre-crossref


# Package Description

This package aims to provide a set of tools for accessing
the Crossref document database through Calibre.

This package is a **work in progress** and, currently,
only a metadata source retriever has been partially implemented.


<a id="install"></a>

# Installation

The simplest way to install this package into Calibre
is through the provided `makefile`, i.e.,
by executing the following shell command
inside the package's root directory:

    make install

Alternatively, you can use Calibre's corresponding tool directly, e.g.:

    calibre-customize -b src/calibre-crossref

Additionally, this package has the following run-time dependencies
which need to be manually installed by the user:

-   `habanero` : Crossref database quering library.

The easiest way of doing so is via `pip` (for `python 2.X`):

    pip2 install habanero           # system wide installation
    pip2 install --user habanero    # installation local to user


# Development and Debugging

In order to debug the provided plugins:

1.  Install the plugins and their dependencies, as described in [3](#install).
2.  Start `calibre` in debug mode, either:
    -   by using the provided `makefile`, e.g.:
        
            make run
    -   by calling the `calibre-customize` tool directly, e.g.:
        
            calibre-degub -g

