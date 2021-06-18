"""
Demodulation pipeline for groundSPEX data
"""

import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
from sys import argv
import groundspex as G

# Get data folder from command-line input
data_folder = Path(argv[1])
print(f"Loading data from {data_folder.absolute()}")

# Load spectra
data = G.load_data_folder(data_folder)
