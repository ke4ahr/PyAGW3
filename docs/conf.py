# Sphinx configuration file for PyAGW3 documentation
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later


import os
import sys
from datetime import datetime

# Add the project root to the path so Sphinx can find the modules
sys.path.insert(0, os.path.abspath('..'))

project = 'PyAGW3'
copyright = f'2025-2026, Kris Kirby, KE4AHR <ke4ahr@gmail.com>'
author = 'Kris Kirby, KE4AHR <ke4ahr@gmail.com>'
release = '0.1.0'
version = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '__init__',
    'inherited-members': True,
    'show-inheritance': True,
}

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
