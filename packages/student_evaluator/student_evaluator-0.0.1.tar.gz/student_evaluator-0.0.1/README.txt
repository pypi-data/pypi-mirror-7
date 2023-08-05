# Student Evaluator
An analysis tool to check the work that student are doing on a linux server.
 * The script creates several user accounts: s1 -> s99
 * The student log in as one of these users
 * Create documents, folders, scripts,.... (as requested in an assignment)
 * The tool scans the filesystem and creates a report (html)
 * The students can see the report semi-live

## Install:
Assuming you start from a basic Debian installation
 * Install Apache webserver: ``aptitude install apache2`` (only needed if you want to show a status report on a website)
 * Install python-pip: ``aptitude install python-pip`` (the Python package manager: https://pypi.python.org/pypi
 * Install using pip: ``pip install student_evaluator``

## Install from source:
 * Download the source and run ``python setup.py install``.
 * Python Package available in the Python Package Index at: (coming soon).

## Usage:
 * Coming soon

## Limitations:
 * Currently under active development (early Alpha!)
 * Not feature complete at all!

## License:
If not stated otherwise student_evaluator is distributed in terms of the MIT software license.
See LICENSE file in the distribution for details.

## Bug reports:
 * Jeroen Doggen <jeroendoggen@gmail.com>
 * Post issues to GitHub https://github.com/jeroendoggen/student-evaluator/issues.

## Changelog:
0.0.1: Basic features
 * Coming soon
