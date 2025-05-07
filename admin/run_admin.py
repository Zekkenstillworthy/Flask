"""
Entry point for the Flask admin application.
Run this script from the root directory to start the admin app.
"""

import os
import sys

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from admin.main import main

if __name__ == "__main__":
    main()
