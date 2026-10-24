"""Classic snake game built on pygame."""

import os

# Keep the pygame banner out of CLI output and test logs.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

__all__ = ["__version__"]

__version__ = "1.1.0"
