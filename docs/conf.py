"""Sphinx documentation, with Markdown guides and Python API references."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
project = "TeamDocs"
author = "Hamza EL JMILI"
copyright = "2026, Hamza EL JMILI"
release = "1.0.0"
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.napoleon"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
html_title = "TeamDocs · The project guide"
html_logo = "_static/mark.svg"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {"style_nav_header_background": "#263c30", "navigation_depth": 2}
autodoc_member_order = "bysource"

