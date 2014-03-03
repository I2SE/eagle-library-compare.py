eagle-library-compare.py
========================

[![Build Status](https://travis-ci.org/I2SE/eagle-library-compare.py.png?branch=master)](https://travis-ci.org/I2SE/eagle-library-compare.py)

Eagle CAD files store all libraries inside the XML files for boards and layouts (.brd and .sch). This tool is to be used to compare these embedded libraries to the external library files (.lbr).

This test is intended to be used in automatic quality assurance systems. You might find it usefull to have a hook of your version control system calling this script on each commit.
