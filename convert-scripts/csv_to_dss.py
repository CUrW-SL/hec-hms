"""
This script should be run via <path-to-hec_hms-home>/dssvue/hec-dssvue.sh
There are several restriction in that python version. Thus this script has been written abiding to those restrictions.
The restrictions are as follows:
    jython version (jython_installer-2.5.0)

Rainfall CSV file format should follow as
https://publicwiki.deltares.nl/display/FEWSDOC/CSV
"""

import java, csv, sys, datetime, re
from hec.heclib.dss import HecDss
from hec.heclib.util import HecTime
from hec.io import TimeSeriesContainer

from optparse import OptionParser

# Passing Commandline Options to Jython. Not same as getopt in python.
# Ref: http://www.jython.org/jythonbook/en/1.0/Scripting.html#parsing-commandline-options
# Doc : https://docs.python.org/2/library/optparse.html
parser = OptionParser(description='Upload CSV data into HEC-HMS DSS storage')
parser.add_option("--csvfp", help="file-path to csv file. csv rainfall file to be converted into DSS format.")
parser.add_option("--dssfp", help="file-path to dss file. where converted dss file should be saved.")

(options, args) = parser.parse_args()
if not options.csvfp and options.dssfp:
    print 'Missing required parameters!'
    print 'Required parameters: dssfp, csvfp'


NUM_METADATA_LINES = 3
try:
    converted_dss = HecDss.open(options.dssfp)

    csv_reader = csv.reader(open(options.csvfp, 'r'), delimiter=',', quotechar='|')
    csv_list = list(csv_reader)

    num_locations = len(csv_list[0]) - 1
    num_values = len(csv_list) - NUM_METADATA_LINES # Ignore Metadata
    location_ids = csv_list[1][1:]

    for i in range(0, num_locations):
        precipitations = []
        for j in range(NUM_METADATA_LINES, num_values + NUM_METADATA_LINES):
            p = float(csv_list[j][i + 1])
            precipitations.append(p)

        tsc = TimeSeriesContainer()
        # tsc.fullName = "/BASIN/LOC/FLOW//1HOUR/OBS/"
        # tsc.fullName = '//' + locationIds[i].upper() + '/PRECIP-INC//1DAY/GAGE/'
        tsc.fullName = '//' + location_ids[i].upper() + '/PRECIP-INC//1HOUR/GAGE/'

        start = HecTime(csv_list[NUM_METADATA_LINES][0])
        tsc.interval = 60  # in minutes
        times = []
        for value in precipitations:
            times.append(start.value())
            start.add(tsc.interval)
        tsc.times = times
        tsc.values = precipitations
        tsc.numberValues = len(precipitations)
        tsc.units = "MM"
        tsc.type = "PER-CUM"
        converted_dss.put(tsc)
finally:
    converted_dss.done()
