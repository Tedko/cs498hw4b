# Simple example of taxiing as scripted behavior
# import Pilot; a=Pilot.Pilot(); a.start()

import ClassCode.Ckpt as Ckpt
import ClassCode.Utilities
import ClassCode.Fgfs
import imp, sys

import HC
import AC



def rel():
    imp.reload(sys.modules['Pilot'])

class Pilot (Ckpt.Ckpt):            # subclass of the class Ckpt in the file Ckpt


    def __init__(sf,tsk='HW4a',rc=False,gui=False):
        super().__init__(tsk, rc, gui)
        sf.hc = HC.Planner()
        sf.ac = AC.AC()
        sf.towerLocation = [37.61703, -122.383585]
        sf.towerAlt = 180 #height of Tower
        sf.flyawayDist = 10000
        sf.planned = False



    def ai(sf,fDat,fCmd):


        #First fly away from Tower, util dist is large enough

        curLocation = [fDat.latitude, fDat.longitude]
        curAlt = fDat.altitude
        distDiff = HC.Pdist(curLocation, sf.towerLocation)
        time = fDat.time

        if(distDiff < sf.flyawayDist ):
            print("distDiff < 10000, fly away",distDiff)
            if not sf.planned:
                if sf.ac.PC(fDat, 2000-curAlt, -10, 200) == 'OK':
                    sf.ac.PLAN(fDat, 2000-curAlt, -10, 200)
                    print('Planned altitude change')
                else:
                    print('Can not achieve target')
                sf.ac.DO(fDat, fCmd)
            # else:
            #     if (sf.ac.DO(fDat, fCmd) == 'DONE') and (distDiff < sf.flyawayDist):
            #         sf.planned = False
            #     else:
            #         print('fly away')


        else:
            print("distDiff > 10000, do next",distDiff)
            return 'stop'

        # when the command list is empty and the last command returns 'DONE'
        # the program exits
        # if(sf.planner.DO(fDat, fCmd) == 'DONE'):
        #     if(len(sf.command) != 0):
        #         pass
        #     else:
        #         return 'stop'
