# Simple example of exploring the flight dynamics
# import ExploringPilot; a=ExploringPilot.ExploringPilot(); a.start()

import ClassCode.Ckpt as Ckpt

import AC

import random, pickle
import imp, sys, math
import time

def rel():
    imp.reload(sys.modules['ACTester'])

class ACTester (Ckpt.Ckpt):            # subclass of the class Ckpt in the file Ckpt

    def __init__(self, tsk = 'HW4a', rc = False, gui = False):
        super().__init__(tsk, rc, gui)
        self.ac = AC.AC()
        self.planned = False

    def ai(self, fDat, fCmd):
        '''Override with the Pilot decision maker, args: fltData and cmdData from Utilities.py'''
        if fDat.time > 5.0:
            if not self.planned:
                if self.ac.PC(fDat, -500, -10, 200) == 'OK':
                    self.ac.PLAN(fDat, -500, -10, 200)
                    self.planned = True
                    print('Planned altitude change')
                else:
                    print('Can not achieve target')
            else:
                if self.ac.DO(fDat, fCmd) == 'DONE':
                    print('Finished maneuver')
                    return 'stop'

ACTester().start()
