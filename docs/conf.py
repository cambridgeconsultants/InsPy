"""Configuration file for the Sphinx documentation builder."""

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
sys.path.append(os.path.abspath(os.path.join(__file__, "../../../inspy")))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "InsPy"
copyright = (
    "2026, Cambridge Consultants Ltd. Licensed under the Apache License, Version 2.0."
)
authors = [
    "Abhishek Ambekar",
    "James Banyard",
    "Oliver Hicks",
    "David Mohamad",
    "Arefin Ahammed",
    "Michal Rajzer",
    "Neel Ramjee",
    "Khushal Bharadwa",
    "Jacky Zheng",
    "Radhika Chandra",
    "David Maynard",
    "Shreyesh Amratlal",
    "Gianluca Andreotti",
    "Logan Baber",
    "Jude Cowden",
    "Ben Goode",
    "Robin Hellen",
    "Simon Hible",
    "Charlie Pentecost",
    "Joshua Perriman",
    "Hatesh Saini",
    "Rachel Weissmandl",
    "Naweed Majeed",
    "Maddy Thackray",
]
author = ", ".join(authors)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": True,
}

myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_favicon = "_static/favicon.png"

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True

autodoc_mock_imports = ["pyvisa", "pyvisa_py", "usb"]

suppress_warnings = ["myst.xref_missing"]
