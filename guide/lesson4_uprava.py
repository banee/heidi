"""
  Lesson 4 - fly forward
"""
import sys
import math
sys.path.append('..') # access to drone source without installation
from ardrone2 import ARDrone2, ManualControlException



def testLesson4_uprava( drone ):

    try:
        drone.takeoff()

        for i in range(4):
            sx, sy, sz, sa = 0.0, 0.0, 0.0, 0.0
            startTime = drone.time
            while drone.time - startTime < 1.5:
                sx = 0.1
                drone.moveXYZA(sx, sy, sz, sa)
            sx=0
            drone.hover(2.0)
            startTime = drone.time
            while drone.time - startTime < 3.0:
                sa = 0.1
                drone.moveXYZA(sx, sy, sz, sa)
            sa=0
            drone.hover(2.0)


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
    launcher.launch( sys.argv, ARDrone2, testLesson4_uprava )


# vim: expandtab sw=4 ts=4

