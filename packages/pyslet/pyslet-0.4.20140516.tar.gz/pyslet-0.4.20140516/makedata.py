#! /usr/bin/env python
"""Script to create static data files."""

import pyslet.unicode5 as unicode5

if __name__ == "__main__":
	unicode5.ParseCategoryTable()
	unicode5.ParseBlockTable()
