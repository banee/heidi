"""
  Lesson 3 - logging examples
"""
import sys
import math

sys.path.append('..') # access to drone source without installation
from ardrone2 import ARDrone2, ManualControlException

def gps_gather2( drone ):
    try:
        if(drone.ctrlState==0):
            drone.reset()

        drone.takeoff()
        drone.hover(2.0)
        print "Battery takeoff: ", drone.battery



        desiredDistance = 1
        realDistance=0
        stage=1

        newX = drone.coord[0]
        newY = drone.coord[1]
        while (realDistance<desiredDistance):
            if(stage==1):
                sx, sy, sz, sa = 0.1, 0.0, 0.0, 0.0
            elif (stage==2):
                sx, sy, sz, sa = 0.0, 0.1, 0.0, 0.0
            elif (stage==3):
                sx, sy, sz, sa = -0.1, 0.0, 0.0, 0.0
            elif (stage==4):
                sx, sy, sz, sa = 0.0, -0.1, 0.0, 0.0
            else:
                break
            drone.moveXYZA( sx, sy, sz, sa )

            #recalculate distance
            x,y,z = drone.coord
            realDistance=math.hypot(x-newX,y-newY)

            if (realDistance>=desiredDistance):
                drone.hover(2.0)
                stage += 1
                realDistance=0
                print math.hypot(x-newX,y-newY)
                newX = drone.coord[0]
                newY = drone.coord[1]
                #GPS printing
                print "Byla dosazena pozadovana vzdalenost"
                print "GPS coordinates: ", drone.gps
                if(drone.gps is not None):
                    lat = drone.gps[0]
                    lon = drone.gps[1]
                    print lat, lon

        drone.hover(2.0)

    except ManualControlException, e:
        print "ManualControlException"
    drone.land()
    print "Battery landing: ", drone.battery



if __name__ == "__main__":
    import launcher
    launcher.launch( sys.argv, ARDrone2, gps_gather2 )


# vim: expandtab sw=4 ts=4

