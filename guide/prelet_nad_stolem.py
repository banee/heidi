"""
  Lesson 4 - fly forward
"""
import sys
import math
sys.path.append('..') # access to drone source without installation
from ardrone2 import ARDrone2, ManualControlException



def prelet_nad_stolem( drone ):

    try:
        print "ctr state ", drone.ctrlState

        if(drone.ctrlState==0):
            drone.reset()

        drone.takeoff()

        z=drone.coord[2]
        while not(z>=0.9 and z<1.1):
            z=drone.coord[2]
            #print z, drone.coord[2], drone.visionTag
            if z<1.4:
                drone.moveXYZA(0, 0, 0.3, 0)
            elif z>1.6:
                drone.moveXYZA(0, 0, -0.3, 0)
            else:
                break

        print "vyska je:", drone.coord[2], drone.visionTag
        drone.hover(2.0)
        height = drone.altitudeData[0]/1000.0
        previousHeight = height

        while (abs(height-previousHeight)<0.5):
            startTime = drone.time
            while drone.time - startTime < 1.5:
                #print "zmena vysky: ",abs(height-previousHeight)
                sx, sy, sz, sa = 0.1, 0.0, 0.0, 0.0
                drone.moveXYZA(sx, sy, sz, sa)
            drone.hover(2.0)
            print "zmena vysky: ",abs(height-previousHeight)
            print drone.altitudeData[0]/1000

            if(abs(height-previousHeight)<0.5):
                while(drone.time - startTime < 1.5):
                    sx, sy, sz, sa = 0.1, 0.0, 0.0, 0.0
                    drone.moveXYZA(sx, sy, sz, sa)
                drone.hover(2.0)

            previousHeight=height
            height=drone.altitudeData[0]/1000.0

        drone.land()

    except ManualControlException, e:
        print "ManualControlException"
    if drone.ctrlState == 3: # CTRL_FLYING=3 ... i.e. stop the current motion
        drone.hover(1.0)
    drone.land()
    x,y,z = drone.coord
    e=math.hypot(x,y)
    print e
    print "Battery", drone.battery
    print "pozice", drone.coord



if __name__ == "__main__":
    import launcher
    launcher.launch( sys.argv, ARDrone2, prelet_nad_stolem )


# vim: expandtab sw=4 ts=4

