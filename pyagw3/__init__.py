# pyagw3/__init__.py File Export

This document provides a full, detailed export of the `pyagw3/__init__.py` file from the PyAGW3 project. It includes the complete source code, explanations of its purpose, structure, and key elements. All placeholders from previous descriptions have been expanded with actual values based on the project's configuration as of December 29, 2025.

## File Overview
- **Path**: `pyagw3/__init__.py`
- **Purpose**: This is the package initialization file for the `pyagw3` Python library. It defines the package's metadata (version, author, license), imports key classes from the core module (`agwpe.py`), and specifies what symbols are exposed when importing the package (via `__all__`).
- **License**: LGPL-3.0-or-later
- **Author**: Kris Kirby, KE4AHR
- **Version**: 0.1.0
- **Dependencies**: None (relies on standard Python libraries like `socket`, `struct`, `threading`, `time`, `logging`, `random`, and `typing`)
- **Role in Project**: Makes the package importable (e.g., `from pyagw3 import AGWPEClient`). It sets up the namespace and provides a docstring for the package.

## Complete Source Code
The following is the exact, unaltered content of `pyagw3/__init__.py`:

    """
    PyAGW3 - Python 3 AGWPE TCP/IP API client library
    Copyright (C) 2025-2026 Kris Kirby, KE4AHR
    License: LGPL-3.0-or-later
    """

    from .agwpe import AGWPEClient, AGWPEFrame

    __version__ = "0.1.0"
    __author__ = "Kris Kirby, KE4AHR"
    __license__ = "GPL-3.0-or-later"
    __all__ = ["AGWPEClient", "AGWPEFrame"]

## Line-by-Line Breakdown
Here is a detailed explanation of each section of the code:

1. **Docstring (Lines 1-4)**:
   - This is a multi-line string providing a brief description of the package, copyright notice, and license. It appears when accessing `help(pyagw3)` or `pyagw3.__doc__`.
   - Expanded details:
     - Description: "PyAGW3 - Python 3 AGWPE TCP/IP API client library"
     - Copyright: "(C) 2025-2026 Kris Kirby, KE4AHR"
     - License: "GPL-3.0-or-later"

2. **Imports (Line 6)**:
   - `from .agwpe import AGWPEClient, AGWPEFrame`
     - This imports the main client class (`AGWPEClient`) and frame structure (`AGWPEFrame`) from the sibling module `agwpe.py` in the same package.
     - The relative import (`.`) ensures it works within the package context.
     - Purpose: Allows users to access these directly via `from pyagw3 import AGWPEClient` without needing to specify the submodule.

3. **Metadata Variables (Lines 8-10)**:
   - `__version__ = "0.1.0"`
     - Defines the package version. Used for versioning in setup tools, documentation, or checks like `pyagw3.__version__`.
   - `__author__ = "Kris Kirby, KE4AHR"`
     - Specifies the author. Useful for attribution in documentation or queries.
   - `__license__ = "GPL-3.0-or-later"`
     - Indicates the license. Matches the project's LICENSE file.

4. **__all__ (Line 11)**:
   - `__all__ = ["AGWPEClient", "AGWPEFrame"]`
     - This list controls what is imported when a user does `from pyagw3 import *`. It exposes only the essential public API, hiding internal details.

## Usage Examples
To demonstrate how this `__init__.py` enables package usage, here are some code snippets:

### Basic Import and Usage
    import pyagw3

    print(pyagw3.__version__)  # Output: 0.1.0
    print(pyagw3.__author__)   # Output: Kris Kirby, KE4AHR

    client = pyagw3.AGWPEClient(host="127.0.0.1", callsign="N0CALL")
    # Proceed with client.connect(), etc.

### Wildcard Import
    from pyagw3 import *

    frame = AGWPEFrame()  # Accessible due to __all__
    client = AGWPEClient()  # Main class

## Integration with Project
- This file is loaded automatically when importing `pyagw3`.
- It assumes `agwpe.py` exists in the same directory, containing the definitions of `AGWPEClient` and `AGWPEFrame`.
- In the full PyAGW3 project, this supports installation via `pip install .`, making the package discoverable and importable system-wide.

## Potential Extensions
If expanding the package:
- Add more imports to `__all__` for new classes.
- Update `__version__` for releases.
- Enhance the docstring with more details or reStructuredText for Sphinx compatibility.

