#!/usr/bin/env python
import argparse
import os
import subprocess
__author__ = "Tarek Taha"
__license__ = "LGPLv3"
__email__ = "tarek@tarektaha.com"
path      = './px4logs/vader/'
outputDir = 'csvlogs/vader/'
for file in os.listdir(path):
    processes = []
    converter = "sdlog2_dump.py"
    if file.endswith(".px4log"):
        print(file)
        cmd = ' '.join(["python", converter, path+file, '>',outputDir + file[:-7] + '.csv'])
        print(cmd)
        processes.append(subprocess.Popen(cmd, shell=True))
    for p in processes:
      p.wait()        