About - Metadata for Setuptools

::

    # about_myproject.py
    """
    My Project Summary

    My Project Description
    """

    metadata = dict(
        __appname__     = "myproject",
        __version__     = "1.0.0",
        __license__     = "MIT License",
        __author__      = u"Sébastien Boisgérault <Sebastien.Boisgerault@gmail.com>",
        __url__         = "https://warehouse.python.org/project/about",
        __doc__         = __doc__,
        __docformat__   = "markdown",
        __classifiers__ = ["Programming Language :: Python :: 2.7",
                           "Topic :: Software Development",
                           "License :: OSI Approved :: MIT License"]
      )

    globals().update(metadata)
    __all__ = metadata.keys()

In ``myproject.py`` just add the following metadata section

::

    # Metadata
    from .about_myproject import *

and in your ``setup.py`` files, use

::

    import setuptools

    import about
    import os
    import path
    sys.path.insert(0, os.getcwd())
    import about_myproject # local version

    info = about.get_metadata(about_myproject)

    # add extra information (contents, requirements, etc.) for the setup.
    info.update(...)

    if __name__ == "__main__":
        setuptools.setup(**info)

