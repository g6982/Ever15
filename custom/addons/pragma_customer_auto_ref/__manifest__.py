# -*- coding: utf-8 -*-
{
    "name": "Automatic Customer Number",
    "version": "1.0.2",
    'license': 'LGPL-3',
    'author': 'Josef Kaser, pragmasoft',
    'website': 'https://www.pragmasoft.de',
    "summary": """
    Automatically create the customer number from a sequence when a customer is being created.
    """,
    "description": """
Automatic Customer Number
=========================
Automatically create the customer number from a sequence when a customer is being created.

The customer number can be configured in the sequence "Customer Number".
    """,
    "category": "Sales",
    "depends": [
        "base",
        "sale",
    ],
    "data": [
        "data/sequencer.xml"
    ],
    "installable": True,
    "auto_install": False,
}
