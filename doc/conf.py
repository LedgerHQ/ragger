# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Ragger'
copyright = '2022, bow'
author = 'bow'


# -- General configuration ---------------------------------------------------

html_favicon = "images/ragger.png"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_copybutton',
    'sphinxcontrib.images',
]

images_config = {
    "default_image_width": "90%",
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

import os
import sys

sys.path.insert(0, os.path.abspath('../src/'))

from importlib.metadata import version as get_version
release = get_version('ragger')
version = '.'.join(release.split('.')[:2])

## Autodoc conf ##

# Do not skip __init__ methods by default
def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

# Remove every module documentation string.
# Prevents to integrate the Licence when using automodule.
# It is possible to limit the impacted module by filtering with the 'name'
# argument:
# `if what == "module" and name in ["ragger.firmware.stax.layouts", ...]:`
def remove_module_docstring(app, what, name, obj, options, lines):
    if what == "module":
        del lines[:]

## Setup ##

def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)
    app.connect("autodoc-skip-member", skip)

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
