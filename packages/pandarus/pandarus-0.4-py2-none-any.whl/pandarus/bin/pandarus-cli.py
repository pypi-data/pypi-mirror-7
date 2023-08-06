#!/usr/bin/env python
# encoding: utf-8
"""Pandarus command line controller.

This program matches two geospatial datasets, and calculates the area of each intersecting spatial unit in map1 and map2.

Usage:
  pandarus <map1> [--field1=<field1>|--band1=<band1>] <map2> [--field2=<field2>|--band2=<band2>] <output> [csv|json|pickle] [options]

Options:
  --no-bz2          Don't compress output with BZip2
  --cpus=<cpus>     Number of cpus to use (default is all)
  --no-projection   Compute areas in CRS of `map2`, don't use Mollweide projection
  -h --help         Show this screen.
  --with-global     Also calculate area of each spatial unit by intersecting with 'GLO', the globe.
  --version         Show version.

"""
from docopt import docopt
from pandarus import *
import os
import sys


def main():
    arguments = docopt(__doc__, version='Pandarus CLI 0.1')
    if False and arguments['info']:
        print Map(arguments['<map>']).info
    else:
        # Set file extension
        output = os.path.abspath(arguments['<output>'])
        json_compression = True

        if arguments['csv']:
            format = 'csv'
        elif arguments['pickle']:
            format = 'pickle'
        else:
            format = 'json'

        if output.split('.')[-1].lower() != format:
            output = output + '.%s' % format

        # Don't overwrite existing output
        if os.path.exists(output) or os.path.exists(output + ".bz2"):
            sys.exit("ERROR: Output file `%s` already exists" % output)

        kwargs = {
            'from_filepath': arguments['<map1>'],
            'to_filepath': arguments['<map2>'],
            'with_global': arguments['--with-global'],
        }
        if arguments.get('--field1'):
            kwargs['from_metadata'] = {'field': arguments['--field1']}
        elif arguments.get('--band1'):
            kwargs['from_metadata'] = {'band': arguments['--band1']}
        if arguments.get('--field2'):
            kwargs['to_metadata'] = {'field': arguments['--field2']}
        elif arguments.get('--band2'):
            kwargs['from_metadata'] = {'band': arguments['--band2']}

        controller = Pandarus(**kwargs)
        controller.match(cpus=int(arguments['--cpus'] or 0))

        if kwargs.get('from_metadata') or controller.from_map.raster:
            controller.add_from_map_fieldname()
        if kwargs.get('to_metadata') or controller.to_map.raster:
            controller.add_to_map_fieldname()

        exported = controller.export(
            output,
            format,
            compress=not arguments['--no-bz2']
        )
        print "Finished Pandarus job; created `%s`" % exported


if __name__ == '__main__':
    main()
