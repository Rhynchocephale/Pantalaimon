#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import pour les images
#import os
#import subprocess
#import shutil
#import hashlib
import Pantalaimon

#import pour le lock
import sys
#import time
import fcntl

file_path = '/var/lock/Pantalaimon.py'
file_handle = open(file_path, 'w')

try:
    fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    logFile = "/tmp/Pantalaimon/Cron.log"
    o = open(logFile,"a")
    o.write(Pantalaimon.now()+" Cron running\n")
    o.close()
    Pantalaimon.launchEverything(logFile)
    

    #Test pour le lock
    #for i in range(100):
    #    time.sleep(1)
    #    print i + 1

#On ne lance pas le Cron si une autre instance run déjà
except IOError:
    print 'another instance is running exiting now'
    sys.exit(0)
