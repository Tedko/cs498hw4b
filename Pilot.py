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
        #sf.towerLocation = [37.61703, -122.383585]

        sf.towerLocation = [37.61701, -122.3836]

        sf.towerAlt = 180 #height of Tower
        sf.flyawayDist = 5000
        sf.levelFlightAlt = 1000
        sf.radius = 1000
        #sf.initLocation = [37.6, -122.34] # dist to T = 4280.936885481255

        sf.firstInitACDone = False
        sf.firstInitACPlaned = False
        sf.firstInitHCDone = False
        sf.firstInitHCPlaned = False


        sf.firstInitHC = True
        sf.initHCdone = False
        sf.levelFlightToInitDone = False
        sf.levelFlightToInitPlaned = False
        sf.flybackInitHC = False
        sf.flybackHCdone = False
        sf.flybackACDone = False
        sf.flybackACPlaned = False
        sf.finalInitHC = False
        sf.finalInitHCDone = False
        sf.finalACDone = False
        sf.finalACPlaned = False
        sf.prevDistDiff = 0
        sf.buzzTowel = False
        sf.buzzInit = True
        sf.prevHeadDiff = 0
        sf.cumHeadDiff = 0
        sf.FinalBuzz = False

        sf.firstACenable = True
        sf.firstHCenable = False

    def ai(sf,fDat,fCmd):

        #First fly away from Tower, to the counter direction of the T
        curLocation = [fDat.latitude, fDat.longitude]
        curAlt = fDat.altitude
        TDistDiff = HC.Pdist(curLocation, sf.towerLocation)
        pHeadtoTower = HC.Pheading(curLocation, sf.towerLocation)

        time = fDat.time
        head = fDat.head
        headDiff = pHeadtoTower - head

        print("=============")
        print("TDistDiff",TDistDiff)
        print("currLocation",curLocation)
        print("=============")

###1st: go to the given alt
        if sf.firstACenable:
            print("##1 go to the given alt")
            if (not sf.firstInitACDone):
                if (not sf.firstInitACPlaned):
                    if sf.ac.PC(fDat, sf.levelFlightAlt-curAlt, -10, 200) == 'OK':
                        sf.ac.PLAN(fDat, sf.levelFlightAlt-curAlt, -10, 200)
                        sf.firstInitACPlaned = True
                        print('Planned altitude change')
                    else:
                        print('Can not achieve target')
                elif sf.ac.DO(fDat, fCmd) == 'DONE' :
                    sf.firstInitACDone = True
                    sf.firstACenable = False

###2nd: chaneg degree:fly opposite to Tower

        # elif (not sf.firstInitHCDone):
        #     if (not sf.firstInitHCPlaned):
        #         if sf.hc.PC(fDat,sf.radius,headDiff+180) == 'OK':
        #             sf.hc.PLAN(fDat,sf.radius,headDiff+180)
        #             sf.firstInitHCPlaned = True
        #             print('Try to trun the init Pt')
        #         else:
        #             print('Try to trun the init Pt,not OK')
        #     elif sf.hc.DO(fDat, fCmd) == 'DONE' :
        #         print('Init Angel Change DONE!')
        #         sf.firstInitHCDone = True


        elif sf.firstInitHC and (not sf.initHCdone):
            #sf.hcInit(fDat,fCmd,headDiff+180,sf.firstInitHC)
            if sf.hc.PC(fDat,sf.radius,headDiff+180) == 'OK':
                sf.hc.PLAN(fDat,sf.radius,headDiff+180)
                sf.firstInitHC = False
                print('Try to trun the init Pt')
            else:
                print('Try to trun the init Pt,not OK')

        elif (not sf.firstInitHC) and (not sf.initHCdone):
            #sf.hcDo(fDat,fCmd,headDiff,sf.initHCdone)
            if sf.hc.DO(fDat, fCmd) == 'DONE' :
                sf.initHCdone = True
                print('Init Angel Change DONE!')


###3rd: level flight

        #now, init angel change done; level flight to the init pt
        elif not sf.levelFlightToInitDone:
            if TDistDiff > sf.flyawayDist :
                sf.levelFlightToInitDone = True
            if not sf.levelFlightToInitPlaned:
                if sf.ac.PC(fDat, sf.levelFlightAlt-curAlt, -10, 200) == 'OK':
                    sf.ac.PLAN(fDat, sf.levelFlightAlt-curAlt, -10, 200,ForeverMode = True)
                    sf.levelFlightToInitPlaned = True
                    print('Planned altitude change,levelFlightToInit')
                else:
                    print('Can not achieve target')
            else:#already planned, level flight DO
                print('fly levelFlight to fly away')
                sf.ac.DO(fDat, fCmd)
                if (TDistDiff > sf.flyawayDist):
                    sf.levelFlightToInitDone = True
                    print('fly back to buzz the TOWER!!')

        #now, levelFlightToInit Done, start fly back to Tower

        #trun back ；head to the tower
        elif (not sf.flybackInitHC) and (not sf.flybackHCdone):
            if sf.hc.PC(fDat,sf.radius,headDiff) == 'OK':
                sf.hc.PLAN(fDat,sf.radius,headDiff)
                sf.flybackInitHC = True
                print('Try to trun to the T,back111!')
        elif (not sf.firstInitHC) and (not sf.flybackHCdone):
            if sf.hc.DO(fDat, fCmd) == 'DONE' :
                sf.flybackHCdone = True
                print('Fly Back Angel Change DONE!')


        #trun to tower done, level flight again!
        elif (not sf.flybackACDone):
            if not sf.flybackACPlaned:
                if sf.ac.PC(fDat, 250-curAlt, -10, 150) == 'OK':
                    sf.ac.PLAN(fDat, 250-curAlt, -10, 150,ForeverMode = True)
                    sf.flybackACPlaned = True
                    print('Planned altitude change,levelFlightToInit')
                else:
                    print('Can not achieve target')
            else:#already planned, level flight DO
                print('Close until 3500')
                sf.ac.DO(fDat, fCmd)
                if (TDistDiff < 3500): #
                    sf.flybackACDone = True
                    print('fly !!!!!')

        #do the final HC adjust
        elif (not sf.finalInitHC) and (not sf.finalInitHCDone):
            if sf.hc.PC(fDat,1000,headDiff) == 'OK':
                sf.hc.PLAN(fDat,1000,headDiff)
                sf.finalInitHC = True
                print('Try to trun to the T,back!')
        elif (not sf.firstInitHC) and (not sf.finalInitHCDone):
            if sf.hc.DO(fDat, fCmd) == 'DONE' :
                sf.finalInitHCDone = True
                print('Last HC Done!')

        #lower, and be closer
        elif (not sf.finalACDone):
            if not sf.finalACPlaned:
                if sf.ac.PC(fDat, 180-curAlt, -10, 150) == 'OK':
                    sf.ac.PLAN(fDat, 180-curAlt, -10, 150,ForeverMode = True)
                    sf.finalACPlaned = True
                    print('Planned altitude change,level f to buzz')
                else:
                    print('Can not achieve target')
            else:#already planned, level flight DO
                print('Close until reach the closest')
                sf.ac.DO(fDat, fCmd)
                if (TDistDiff < 700): #
                    sf.flybackACDone = True
                    sf.buzzTowel = True
                    print('fly !!!!!reach the closest')


        if sf.buzzTowel:
            if sf.buzzInit:
                sf.hc.PLAN(fDat,1000,headDiff)
                sf.buzzInit = False
            elif sf.hc.DO(fDat, fCmd) == 'DONE' :
                sf.FinalBuzz = True
                print('Last HC Done!')
            #here buzz T

            # diff = sf.prevHeadDiff - headDiff
            # if diff > 180:
            #     diff = diff -360
            # elif diff < -180 :
            #     diff = diff +360
            # fCmd.aileron = 0.7
            # sf.cumHeadDiff += diff
            # if sf.cumHeadDiff > 450 :
            #     return 'stop'


        sf.prevDistDiff = TDistDiff
        sf.prevHeadDiff = headDiff


    def hcInit(sf,fDat,fCmd,headDiff,initDone):
        if sf.hc.PC(fDat,sf.radius,headDiff) == 'OK':
            sf.hc.PLAN(fDat,sf.radius,headDiff)
            initDone = not initDone
            print('Try to trun !')
        else :
            print('HC init input Err!')

    def hcDo(sf,fDat,fCmd,headDiff,doDone):
        if sf.hc.DO(fDat, fCmd) == 'DONE' :
            doDone = not doDone
            print('HC DONE!')
