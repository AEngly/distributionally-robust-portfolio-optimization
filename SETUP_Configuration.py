"""
File: SETUP_SolverConfiguration.py
Author: Andreas Engly
Date: 30-11-2023
Description: This notebook follows the tutorial on MOSEK's website: https://docs.mosek.com/10.0/install/installation.html.
             Subsequently place the directory in a folder called "Solvers.

Dependencies:
- See below.

Usage:
- Run the file without any arguments.

Note:
- No additional notes.

"""

# Dependencies
import os

# Run the installation
os.system("Solvers/mosek/10.0/tools/platform/osxaarch64/bin/install.py")

# Install optimization suite
os.system("pip install Mosek");

