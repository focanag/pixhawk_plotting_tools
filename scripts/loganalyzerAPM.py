#!/usr/bin/env python
import argparse
import os
import subprocess
__author__ = "Thomas Gubler"
__license__ = "BSD"
__email__ = "thomasgubler@gmail.com"


class LogAnalyzer():
    """A class that helps anaylze logs"""

    def __init__(self, args):
        """Constructor"""
        self.filenames = args.filenames
        if args.legend:
            self.legendCmd = ''.join(["--legend=\"", args.legend, '\"'])
        else:
            self.legendCmd = ''
        self.mavgraph = "/usr/local/bin/mavgraph.py"
        self.mavgraphOptions = "--flightmode=apm"
        #self.plots = {"Altitude": "GPS.Alt GPS.RelAlt CTUN.WPAlt CTUN.BarAlt",
        #              "Roll": "ATT.Roll ATSP.RollSP",
        #              "Pitch": "ATT.Pitch ATSP.PitchSP",
        #              "Lat": "GPS.Lat GPOS.Lat GPSP.Lat",
        #              "Lon": "GPS.Lng",
        #              "Alt": "GPS.Alt GPS.nSat STAT.MainState"}
        # magField = sqrt(MAG.MagX^2+MAG.MagY^2+MAG.MagZ^2)
        self.plots = {"Altitude": "GPS.Alt GPS.RelAlt CMD.Alt CTUN.BarAlt",
		      "Attitude-ROLL": "ATT.Roll ATT.DesRoll",
		      "Attitude-PITCH": "ATT.Pitch ATT.DesPitch",
		      "Attitude-YAW": "ATT.Yaw ATT.DesYaw",
		      "IMU-ACC": "IMU.AccX IMU.AccY IMU.AccZ",
		      "MAG": "MAG.MagX MAG.MagY MAG.MagZ",
		      "MAG-Offset": "MAG.OfsX MAG.OfsY MAG.OfsZ",
		      "GPS": "GPS.NSats GPS.HDop",
		      "POWER": "POWR.Vcc CURR.ThrOut CTUN.ThrIn CTUN.ThrOut",
		      #"Error": "ERR.Subsys",
		      "RC-OUT": "RCOU.Chan1 RCOU.Chan2 RCOU.Chan3 RCOU.Chan4 RCOU.Chan5 RCOU.Chan6 RCOU.Chan7 RCOU.Chan8",
		      "RC-IN": "RCIN.C1 RCIN.C2 RCIN.C3 RCIN.C4 RCIN.C5 RCIN.C6 RCIN.C7 RCIN.C8"
		     }

    def generatePlots(self, filename, dirname):
        """produce plots for filename in dirname"""
        print(' '.join(["Analyzing ", filename]))

        processes = []
        for plotTitle, plotFields in self.plots.items():
            plotFileName = ''.join([filename, '_', plotTitle, ".png"])
            output = ''.join(["--output=", dirname, "/", plotFileName])
            cmd = ' '.join(["python2", self.mavgraph, self.mavgraphOptions,
                            self.legendCmd, output, plotFields, filename])
            processes.append(subprocess.Popen(cmd, shell=True))

        # wait for the mavgraph processes to finish before continuing
        for p in processes:
            p.wait()

    def createOutputdir(self, filename):
        """Creates the output directory given the filename"""
        dirname = filename[:-4]
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        else:
            print(' '.join([dirname, "already exists, continuing..."]))

        return dirname

    def analyze(self):
        """runs analysis for each file in filenams"""
        for f in self.filenames:
            # create output dir
            dirname = self.createOutputdir(f)

            # generate a set of plots
            self.generatePlots(f, dirname)


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Log analyzation tool')
    parser.add_argument('--legend', dest='legend', default='lower right',
                        action='store', help='legend position (matplotlib)')
    parser.add_argument(dest='filenames', default='', action='store',
                        help='Filenames of logfiles', nargs='+')

    args = parser.parse_args()

    analyzer = LogAnalyzer(args)
    analyzer.analyze()
