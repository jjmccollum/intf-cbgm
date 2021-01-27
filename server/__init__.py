"""This package implements the application server for CBGM.

"""
import os
import sys
# add this dir to PYTHONPATH; on live server this is handled via systemctl
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
