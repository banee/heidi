"""
  Lesson 4 - fly forward
"""
import sys
import math
sys.path.append('..') # access to drone source without installation
from ardrone2 import ARDrone2, ManualControlException

def difangles(alfa, beta):
    c=alfa-beta
    while(c>math.pi):
        c-=math.pi*2
    while(c<-math.pi):
        c+=math.pi*2
    return c


def testLesson4( drone ):
    d=None
    try:
        drone.takeoff()


        z=drone.coord[2]
        while not(z>=1.4 and z<1.6):
            z=drone.coord[2]
            print z, drone.coord[2], drone.visionTag
            if z<1.4:
                drone.moveXYZA(0, 0, 0.3, 0)
            elif z>1.6:
                drone.moveXYZA(0, 0, -0.3, 0)
            else:
                break

        while(abs(difangles(drone.heading, math.radians(90)))>math.radians(10)):
            angle = difangles(drone.heading, math.radians(90))
            if(angle<math.radians(0)):
                drone.moveXYZA(0, 0, 0, 0.1)
            elif(angle>math.radians(0)):
                drone.moveXYZA(0, 0, 0, -0.1)
            else:
                break

        startTime = drone.time
        while drone.time - startTime < 4.0:
            sx, sy, sz, sa = 0.1, 0.0, 0.0, 0.0
            drone.moveXYZA( sx, sy, sz, sa )
            print math.degrees(drone.heading), drone.headingOffset
            x,y,z = drone.coord
            d=math.hypot(x,y)
            #print d
            if d>2:
                print "podmika ", d
                break
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
    launcher.launch( sys.argv, ARDrone2, testLesson4 )


# vim: expandtab sw=4 ts=4

