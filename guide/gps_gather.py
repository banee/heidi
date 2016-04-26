"""
  Lesson 3 - logging examples
"""
import sys
sys.path.append('..') # access to drone source without installation
from ardrone2 import ARDrone2, ManualControlException

def gps_gather( drone ):
    try:
        if(drone.ctrlState==0):
            drone.reset()

        drone.takeoff()
        drone.hover(2.0)
        print "Battery takeoff: ", drone.battery


        a = 2.0
        b=a+1.0
        startTime = drone.time
        while drone.time - startTime < a:
                #print "zmena vysky: ",abs(height-previousHeight)
            sx, sy, sz, sa = 0.1, 0.0, 0.0, 0.0
            drone.moveXYZA(sx, sy, sz, sa)
            drone.moveXYZA(0, 0, 0, 0)
        while drone.time - startTime < b:
                #print "zmena vysky: ",abs(height-previousHeight)
            drone.moveXYZA(0.0, 0.0, 0.0, 0.0)
        drone.hover(2.0)

        startTime = drone.time
        while drone.time - startTime < a:
                #print "zmena vysky: ",abs(height-previousHeight)
            sx, sy, sz, sa = 0, 0.1, 0.0, 0.0
            drone.moveXYZA(sx, sy, sz, sa)
        while drone.time - startTime < b:
                #print "zmena vysky: ",abs(height-previousHeight)
            drone.moveXYZA(0.0, 0.0, 0.0, 0.0)
        drone.hover(2.0)

        startTime = drone.time
        while drone.time - startTime < a:
                #print "zmena vysky: ",abs(height-previousHeight)
            sx, sy, sz, sa = -0.1, 0.0, 0.0, 0.0
            drone.moveXYZA(sx, sy, sz, sa)
        while drone.time - startTime < b:
                #print "zmena vysky: ",abs(height-previousHeight)
            drone.moveXYZA(0.0, 0.0, 0.0, 0.0)
        drone.hover(2.0)

        startTime = drone.time
        while drone.time - startTime < a:
                #print "zmena vysky: ",abs(height-previousHeight)
            sx, sy, sz, sa = 0, -0.1, 0.0, 0.0
            drone.moveXYZA(sx, sy, sz, sa)
        while drone.time - startTime < b:
                #print "zmena vysky: ",abs(height-previousHeight)
            drone.moveXYZA(0.0, 0.0, 0.0, 0.0)
        drone.hover(2.0)


    except ManualControlException, e:
        print "ManualControlException"
    drone.land()
    print "Battery landing: ", drone.battery



if __name__ == "__main__":
    import launcher
    launcher.launch( sys.argv, ARDrone2, gps_gather )


# vim: expandtab sw=4 ts=4

