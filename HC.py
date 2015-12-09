import math
import PID

class Planner:

    def __init__(sf):

        sf.prevTime = 0.0
        sf.speedPID = PID.PID( 0.027,0.005,0.0005 )
        sf.pitchPID = PID.PID( 0.04,0.0054,0.005 )
        sf.rollPID = PID.PID( 0.01,0.001,0.0036 )
        sf.headPID = PID.PID( 2,0.4,0.36 )

        sf.destSpeed = 110.0
        sf.destPitch = 1.0
        sf.destRoll = 0.0
        sf.destHeading = 0.0
        sf.turningCenter = [0,0]

        sf.validateHeading = False
        sf.validateStartTime = 0

        sf.aileronRollStartTime = 0
        sf.arstart = False
        sf.Victory = False

    def PC(sf, fDat, radius, angle):
        angle = angle % 360
        if(radius >= 1000 and angle <= 355):
            return 'OK'
        else:
            return [1000,355]


    def PLAN(sf, fDat, radius, angle):
        curHeading = fDat.head
        sf.rightTurn = radius > 0
        sf.radius = radius

        if(sf.rightTurn):
            sf.destHeading = (curHeading + angle)%360
        else:
            sf.destHeading = (curHeading - angle)%360

        curLocation = [fDat.latitude, fDat.longitude]
        sf.turningCenter = findCenter(curHeading, curLocation, radius)
        sf.turning = True

        sf.headPID.pidClear()

        return

    def DO(sf,fDat, fCmd):
        if(sf.prevTime == fDat.time): #if the same package, skip
            return'SAMEPACKAGE'
        else:
            timeDiff = fDat.time-sf.prevTime
            speed = fDat.kias
            pitch = fDat.pitch
            roll = fDat.roll

            #speed and pitch PID control
            speedPIDRet = sf.speedPID.pid(sf.destSpeed-speed,timeDiff)
            pitchPIDRet = sf.pitchPID.pid(sf.destPitch-pitch,timeDiff)

            fCmd.throttle = speedPIDRet
            print('throttle', speedPIDRet)
            fCmd.elevator = -pitchPIDRet
            print('pitch', pitch)
            print('elavator', pitchPIDRet)
            print('altitude', fDat.altitude)

            print('=========')


            # heading and roll PID control
            curHeading = fDat.head;
            curLocation = [fDat.latitude, fDat.longitude]

            headDiff = (sf.destHeading-curHeading)%360

            if (headDiff > 180):
                headDiff = headDiff - 360

            print('destHeading', sf.destHeading)
            print('curHeading', curHeading)
            print('headDifffirst', headDiff)

            print('distToCenter', Pdist(curLocation, sf.turningCenter))

            if(math.fabs(headDiff)<2):
                sf.turning = False
                if(not sf.validateHeading):
                    sf.validateStartTime = fDat.time
                sf.validateHeading = True
            else:
                sf.validateHeading = False


            # done when plane in destination heading for more than 6 seconds
            print('timediff', (fDat.time-sf.validateStartTime))
            if(sf.validateHeading and fDat.time-sf.validateStartTime > 6):
                return 'DONE'

            if(sf.turning):
                tempHeading = Pheading(curLocation, sf.turningCenter)

                if(sf.rightTurn):
                    tempHeading -= 90
                else:
                    tempHeading += 90

                tempHeading = tempHeading%360

                print('tempHeading', tempHeading)

                headDiff = (tempHeading-curHeading)%360

            if (headDiff > 180):
                headDiff = headDiff - 360


            print('headDiffTurning', headDiff*1.5)



            destRoll = sf.headPID.pid(headDiff*1.2, timeDiff)
            print('destRoll', destRoll)
            print('roll', roll)


            rollPIDRet = sf.rollPID.pid(destRoll-roll,timeDiff)

            fCmd.aileron = rollPIDRet
            print('aileron', rollPIDRet)

            #update variables
            sf.prevTime = fDat.time
            print('==========================================================')

            return 'CONTINUE'


    def BuzzL(sf,fDat, fCmd):
        if(sf.prevTime == fDat.time): #if the same package, skip
            return'SAMEPACKAGE'
        else:
                sf.BuzzStartTime = fDat.time

                timeDiff = fDat.time-sf.prevTime
                timer = fDat.time - sf.BuzzStartTime

                pitch = fDat.pitch
                roll = fDat.roll

                pitchPIDRet = sf.pitchPID.pid(0.0-pitch,timeDiff)
                rollPIDRet = sf.rollPID.pid(0.0-roll,timeDiff)

                print('timer', timer)

                starttime = 0

                if(timer >= starttime and timer<starttime+0.8):
                    fCmd.aileron = 1.0
                # elif(timer >= starttime+2.8 and timer<starttime+3.4):
                #     fCmd.aileron = -1.0
                elif(timer >= 10):
                    return 'DONE'
                else:
                    fCmd.aileron = rollPIDRet
                    fCmd.elevator = -pitchPIDRet

                sf.prevTime = fDat.time



    def AileronRoll(sf,fDat, fCmd):

        if(sf.prevTime == fDat.time): #if the same package, skip
            return'SAMEPACKAGE'
        else:
            if(sf.Victory):
                if(not sf.arstart):
                    sf.aileronRollStartTime = fDat.time
                    sf.arstart = True

                timeDiff = fDat.time-sf.prevTime
                timer = fDat.time - sf.aileronRollStartTime

                pitch = fDat.pitch
                roll = fDat.roll

                pitchPIDRet = sf.pitchPID.pid(0.0-pitch,timeDiff)
                rollPIDRet = sf.rollPID.pid(0.0-roll,timeDiff)

                print('timer', timer)


                starttime = 10

                if(timer >= starttime and timer<starttime+2.8):
                    fCmd.aileron = 1.0
                elif(timer >= starttime+2.8 and timer<starttime+3.4):
                    fCmd.aileron = -1.0
                elif(timer >= 25):
                    return 'DONE'
                else:
                    fCmd.aileron = rollPIDRet
                    fCmd.elevator = -pitchPIDRet

                sf.prevTime = fDat.time





#find center of banking based on current location and turning radius
# if right turn, the origin will be at 90 degress to the right of current location
# and radius distance, vice versa
def findCenter(curHeading, curLocation, radius):

    if(radius>0):
        curHeading += 90
    else:
        curHeading -= 90
    curHeading = curHeading%360

    return destPoint(curLocation, curHeading, math.fabs(radius))

# calculate destination point based on startPoint, bearing and distance
# based on http://www.movable-type.co.uk/scripts/latlong.html
# returns destination point in longitude and latitude
def destPoint(startPoint, bearing, distance):

    print("startPoint", startPoint[0],"::", startPoint[1])
    print('bearing', bearing)
    print('distance', distance)

    R = 6371000.0 #earth's radius
    phi1 = math.radians(startPoint[0])
    slambda1 = math.radians(startPoint[1])
    theta = math.radians(bearing)
    delta = distance/R

    phi2 = math.asin( math.sin(phi1) * math.cos(delta) + math.cos(phi1) * math.sin(delta) * math.cos(theta) )
    y = math.sin(theta) * math.sin(delta) * math.cos(phi1)
    x = math.cos(delta) - math.sin(phi1) * math.sin(phi2)
    slambda2 = slambda1 + math.atan2(y,x)

    endPoint = [math.degrees(phi2), math.degrees(slambda2)]
    print("endPoint", endPoint[0],"::", endPoint[1])

    return endPoint

# distance function based on http://www.movable-type.co.uk/scripts/latlong.html
# distance in meters
def Pdist(lli,llf):
    R = 6371000.0 #earth's radius
    theta1 = math.radians(lli[0])
    theta2 = math.radians(llf[0])
    dtheta = math.radians(llf[0] - lli[0])
    dlambda = math.radians(llf[1] - lli[1])

    a = math.sin(dtheta/2.0) * math.sin(dtheta/2.0) + math.cos(theta1) * math.cos(theta2) * math.sin(dlambda/2.0) * math.sin(dlambda/2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c

    return d

# heading function based on http://www.movable-type.co.uk/scripts/latlong.html
# heading in degrees, north being 0
def Pheading(lli, llf):
    theta1 = math.radians(lli[0])
    theta2 = math.radians(llf[0])
    lambda1 = math.radians(lli[1])
    lambda2 = math.radians(llf[1])
    dtheta = math.radians(llf[0] - lli[0])
    dlambda = math.radians(llf[1] - lli[1])

    y = math.sin(lambda2 - lambda1) * math.cos(theta2)
    x = math.cos(theta1) * math.sin(theta2) - math.sin(theta1) * math.cos(theta2) * math.cos(lambda2 - lambda1)

    heading = math.degrees(math.atan2(y, x))%360.0

    return heading
