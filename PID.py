import imp, sys

class PID ():

    def __init__(sf,coeffP,coeffI,coeffD):
        sf.coeffP = coeffP
        sf.coeffI = coeffI
        sf.coeffD = coeffD
        sf.prevError = 0
        sf.integral = 0

    def pid(sf,error,timeDiff):
        derivative = (error-sf.prevError)/timeDiff
        sf.integral += (sf.prevError+error)*timeDiff/2*0.9
        ret = error*sf.coeffP + sf.integral*sf.coeffI + derivative*sf.coeffD

        sf.prevError = error
        return ret

    def pidClear(sf):
        sf.integral = 0
        sf.prevError = 0
