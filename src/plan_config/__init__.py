"""Northwind plan configuration: the published source of truth for benefit plans.

The JSON under ``config/`` is the product database. The modules in this package
load it, seed it into Postgres, and serve it to the enrollment experience.
"""

__version__ = "2027.1.0"
