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

project = 'doppkit-esri-toolbox'
copyright = '2023, Hobu Inc.'
author = 'Ognyan Moore'

# get version info without installing
import importlib.util
import sys
import pathlib
spec = importlib.util.spec_from_file_location(
	"doppkit_toolbox",
	pathlib.Path("../src/doppkit_toolbox/__init__.py").resolve()
)
doppkit_toolbox = importlib.util.module_from_spec(spec)
sys.modules["doppkit_toolbox"] = doppkit_toolbox
spec.loader.exec_module(doppkit_toolbox)


# The full version, including alpha/beta/rc tags
release = doppkit_toolbox.__version__

from packaging.version import parse
version = parse(release).public


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
	"myst_parser"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for LATEX output ------------------------------------------------

latex_elements = {
	'extraclassoptions': ',oneany,oneside',
	'papersize': 'letterpaper',
}

pygments_style = "staroffice"