"""
  Lesson 3 - logging examples
"""
import sys
import math

sys.path.append('..') # access to drone source without installation
from ardrone2 import ARDrone2, ManualControlException

def gps_distance( drone ):
    try:
        if(drone.ctrlState==0):
            drone.reset()

        drone.takeoff()
        drone.hover(2.0)
        print "Battery takeoff: ", drone.battery



        s1 = 50.1284499
        d1 = 14.3760727

        s2 = 50.1284599
        d2 = 14.3760629

        # Return value in meters
        distanceGPS=math.acos(math.cos(math.radians(90-s1))*math.cos(math.radians(90-s2))+math.sin(math.radians(90-s1))*math.sin(math.radians(90-s2))*math.cos(math.radians(d1-d2)))*6371
        print "!!!!!!!!!!!!!!!!!!!!! TESTOVACI HODNOTA1 ", distanceGPS*1000


        desiredDistance = 1
        realDistance=0
        stage=1

        lastX = drone.coord[0]
        lastY = drone.coord[1]

        lastGPSLat = drone.gps[0]
        lastGPSLon = drone.gps[1]

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
            realDistance=math.hypot(x-lastX,y-lastY)

            if (realDistance>=desiredDistance):
                distanceGPS=math.acos(math.cos(math.radians(90-drone.gps[0]))*math.cos(math.radians(90-lastGPSLat))+math.sin(math.radians(90-drone.gps[0]))*math.sin(math.radians(90-lastGPSLat))*math.cos(math.radians(drone.gps[1]-lastGPSLon)))*6371
                print "!!!!!!!!!!!!!!!!!!!!! TESTOVACI HODNOTA1 ", distanceGPS*1000
                #pokus o vyuziti funkce - nefungovalo
                #aa= distanceGPS(drone.gps[0], drone.gps[1], lastGPSLat, lastGPSLon)
                #print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA ", aa
                drone.hover(2.0)
                stage += 1
                realDistance=0
                print math.hypot(x-lastX,y-lastY)
                lastX = drone.coord[0]
                lastY = drone.coord[1]
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


# nefungovalo - nemohu volat float
def distanceGPS(s1, d1, s2, d2):
    # Return value in meters
    distanceGPS=math.acos(math.cos(math.radians(90-s1))*math.cos(math.radians(90-s2))+math.sin(math.radians(90-s1))*math.sin(math.radians(90-s2))*math.cos(math.radians(d1-d2)))*6371
    print "!!!!!!!!!!!!!!!!!!!!! TESTOVACI HODNOTA1 ", distanceGPS*1000
    return distanceGPS

if __name__ == "__main__":
    import launcher
    launcher.launch( sys.argv, ARDrone2, gps_distance )


# vim: expandtab sw=4 ts=4

