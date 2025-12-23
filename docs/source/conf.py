"""Sphinx configuration for django-model-changes documentation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure Django settings if not already configured
from django.conf import settings

if not settings.configured and not os.environ.get("DJANGO_SETTINGS_MODULE"):
    settings.configure()

from django_model_changes import __version__

# -- Project information -------------------------------------------------------

project = "django-model-changes"
copyright = "2013-2025, Robert Kajic"
author = "Robert Kajic"
version = __version__
release = __version__

# -- General configuration -----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns: list[str] = []
pygments_style = "sphinx"

# -- Options for HTML output ---------------------------------------------------

html_theme = "alabaster"
html_static_path = ["_static"]
htmlhelp_basename = "django-model-changesdoc"

# -- Options for LaTeX output --------------------------------------------------

latex_documents = [
    (
        "index",
        "django-model-changes.tex",
        "django-model-changes Documentation",
        "Robert Kajic",
        "manual",
    ),
]

# -- Options for manual page output --------------------------------------------

man_pages = [
    (
        "index",
        "django-model-changes",
        "django-model-changes Documentation",
        ["Robert Kajic"],
        1,
    )
]

# -- Options for Texinfo output ------------------------------------------------

texinfo_documents = [
    (
        "index",
        "django-model-changes",
        "django-model-changes Documentation",
        "Robert Kajic",
        "django-model-changes",
        "Track model instance changes in Django.",
        "Miscellaneous",
    ),
]

# -- Extension configuration ---------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/stable/", None),
}
