"""
This script should be run via <path-to-hec_hms-home>/dssvue/hec-dssvue.sh
There are several restriction in that python version. Thus this script has been written abiding to those restrictions.
The restrictions are as follows:
    jython version (jython_installer-2.5.0)
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
parser.add_option("--dssfp", help="file-path to dss file. dss file from which Flow should be extracted.")
parser.add_option("--csvfp", help="file-path to csv file. where csv Flow file should be stored.")

(options, args) = parser.parse_args()
if not options.csvfp and options.dssfp:
    print 'Missing required parameters!'
    print 'Required parameters: csvfp, dssfp'

NUM_METADATA_LINES = 2
try:
    output_dss = HecDss.open(options.dssfp)

    flow = output_dss.get('//HANWELLA/FLOW//1HOUR/RUN:RUN 1/', 1)
    if flow.numberValues == 0:
        print 'No Flow Data! Exiting the program...'
        exit(1)
    else:
        csv_writer = csv.writer(open(options.csvfp, 'w'), delimiter=',', quotechar='|')

        # Writing meta data.
        csv_writer.writerow(['Location Ids', 'Hanwella'])
        csv_writer.writerow(['Time', 'Flow'])

        csv_list = []
        for i in range(0, flow.numberValues):
            time = HecTime()
            time.set(int(flow.times[i]))

            d = [time.year(), '%d' % (time.month(),), '%d' % (time.day(),)]
            t = ['%d' % (time.hour(),), '%d' % (time.minute(),), '%d' % (time.second(),)]
            if int(t[0]) > 23:
                t[0] = '23'
                dtStr = '-'.join(str(x) for x in d) + ' ' + ':'.join(str(x) for x in t)
                dt = datetime.datetime.strptime(dtStr, '%Y-%m-%d %H:%M:%S')
                dt = dt + datetime.timedelta(hours=1)
            else:
                dtStr = '-'.join(str(x) for x in d) + ' ' + ':'.join(str(x) for x in t)
                dt = datetime.datetime.strptime(dtStr, '%Y-%m-%d %H:%M:%S')

            csv_list.append([dt.strftime('%Y-%m-%d %H:%M:%S'), "%.2f" % flow.values[i]])
        csv_writer.writerows(csv_list)
finally:
    output_dss.done()