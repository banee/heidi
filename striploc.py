"""
  Strips Localisation for Air Race
"""
from pose import Pose
from airrace import PATH_TURN_LEFT, PATH_TURN_RIGHT, PATH_STRAIGHT
import math

class StripsLocalisation:
  def __init__( self ):
    self.basePose = Pose()
    self.lastStripPose = None
    self.pathType = PATH_TURN_LEFT

  
  def filterPose( self, pose ):
    return pose.sub( self.basePose )

  def updateFrame( self, pose, frameStrips ):
    print [str(p) for p in frameStrips]
    for i in xrange(len(frameStrips)):
      for j in xrange(len(frameStrips)):
        if i != j:
          (dx,dy,da) = frameStrips[i].sub(frameStrips[j])
          if (0.35 < dx < 0.45) and abs(da) < math.radians(50):
            if abs(da) < math.radians(10):
              self.pathType = PATH_STRAIGHT
            elif da > 0:
              self.pathType = PATH_TURN_LEFT
            else:
              self.pathType = PATH_TURN_RIGHT

    for fs in frameStrips:
      sPose = pose.add( fs )
      if self.lastStripPose != None:
        print sPose.sub( self.lastStripPose )
      self.lastStripPose = sPose
