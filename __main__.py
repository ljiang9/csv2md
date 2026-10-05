"""python -m csv2md 入口。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from csv2md import main

if __name__ == "__main__":
    sys.exit(main())
