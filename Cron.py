#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import pour les images
import Pantalaimon
import os

#import pour le lock
import sys
import time
import fcntl

file_path = '/var/lock/test.py'
file_handle = open(file_path, 'w')

try:
    logFile = "/tmp/Pantalaimon/Cron.log"
    Pantalaimon.launchEverything(logFile)
    
    #Test unitaire pour le lock
    #for i in range(100):
    #    time.sleep(1)
    #    print i + 1

#On ne lance pas le Cron si une autre instance run déjà
except IOError:
    print 'another instance is running exiting now'
    sys.exit(0)
