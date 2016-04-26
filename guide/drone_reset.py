"""
  Lesson 3 - logging examples
"""
import sys
sys.path.append('..') # access to drone source without installation
from ardrone2 import ARDrone2, ManualControlException

def drone_reset( drone ):
    try:
        if(drone.ctrlState==0):
            drone.reset()

    except ManualControlException, e:
        print "ManualControlException"
    drone.land()
    print "Battery landing: ", drone.battery



if __name__ == "__main__":
    import launcher
    launcher.launch( sys.argv, ARDrone2, drone_reset )


# vim: expandtab sw=4 ts=4

