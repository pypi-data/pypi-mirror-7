Address Parser
======================

Yet another python address parser. 

    from address_parser import Parser
    import csv

    parser = Parser()

    ps = parser.parse('1089-1099 Carlsbad Village Dr, Carlsbad, CA')

    print ps.dict # Dictionary form, with all components

    print ps.args # Simple dictionary, for use in arguments lists. 

A complete dictionary output looks like:

    {'hash': '34c56b214a1dd719227f829278755d1b',
     'locality': {'city': 'Carlsbad', 'state': 'CA', 'type': 'P', 'zip': None},
     'number': {'end_number': None,
                'fraction': None,
                'is_block': False,
                'number': 1089,
                'suite': None,
                'tnumber': '1089',
                'type': 'P'},
     'road': {'direction': '',
              'name': 'Carlsbad Village',
              'suffix': 'Dr',
              'type': 'P'},
     'text': '1089 Carlsbad Village Dr, Carlsbad, CA'}
     
The argument form looks like: 

    {'city': 'Carlsbad',
     'direction': '',
     'name': 'Carlsbad Village',
     'number': 1089,
     'state': 'CA',
     'suffix': 'Dr',
     'zip': None}
