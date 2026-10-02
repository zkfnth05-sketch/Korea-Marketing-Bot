# -*- coding: utf-8 -*-
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "kmarket-marketing-engine"
sys.path.insert(0, str(BASE_DIR))

from brands.insurance.insurance_reddit_login import main

if __name__ == "__main__":
    main()
