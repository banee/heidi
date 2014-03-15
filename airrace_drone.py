#!/usr/bin/python
"""
  AirRace competition in Vienna. See robotchallenge.org
  usage:
       ./airrace.py <TODO>
"""
import sys
import datetime
import multiprocessing
import cv2
import math
from pave import PaVE, isIFrame, frameNumber, timestamp, correctTimePeriod
from airrace import processFrame, filterRectangles, stripPose, classifyPath
from airrace import PATH_UNKNOWN, PATH_STRAIGHT, PATH_CROSSING, PATH_TURN_LEFT, PATH_TURN_RIGHT
from sourcelogger import SourceLogger
from ardrone2 import ARDrone2, ManualControlException, manualControl, normalizeAnglePIPI, distance
import viewlog
from line import Line
from pose import Pose

REF_CIRCLE_RADIUS = 1.4 # TODO measure in real arena!
REF_LINE_CROSSING_ANGLE = math.radians(50) # angle for selection of proper strip
TRANSITION_RADIUS = 2.15 # TODO measure - distance from crossing to circle tangent point
CROSSING_Y_COORD = 1.4+2.45 # TODO measure

def timeName( prefix, ext ):
  dt = datetime.datetime.now()
  filename = prefix + dt.strftime("%y%m%d_%H%M%S.") + ext
  return filename

g_pave = None

def wrapper( packet ):
  global g_pave
  if g_pave == None:
    g_pave = PaVE()
  g_pave.append( packet )
  header,payload = g_pave.extract()
  while payload:
    if isIFrame( header ):
      tmpFile = open( "tmp.bin", "wb" )
      tmpFile.write( payload )
      tmpFile.flush()
      tmpFile.close()
      cap = cv2.VideoCapture( "tmp.bin" )
      ret, frame = cap.read()
      assert ret
      if ret:
        return (frameNumber( header ), timestamp(header)), processFrame( frame, debug=False )
    header,payload = g_pave.extract()

g_queueResults = multiprocessing.Queue()

def getOrNone():
  if g_queueResults.empty():
    return None
  return g_queueResults.get()


class AirRaceDrone( ARDrone2 ):
  def __init__( self, replayLog=None, speed = 0.2, skipConfigure=False, metaLog=None, console=None ):
    self.loggedVideoResult = None
    self.lastImageResult = None
    self.videoHighResolution = False
    ARDrone2.__init__( self, replayLog, speed, skipConfigure, metaLog, console )
    if replayLog == None:
      name = timeName( "logs/src_cv2_", "log" ) 
      metaLog.write("cv2: "+name+'\n' )
      self.loggedVideoResult = SourceLogger( getOrNone, name ).get
      self.startVideo( wrapper, g_queueResults, record=True, highResolution=self.videoHighResolution )
    else:
      assert metaLog
      self.loggedVideoResult = SourceLogger( None, metaLog.getLog("cv2:") ).get
      self.startVideo( record=True, highResolution=self.videoHighResolution )

  def update( self, cmd="AT*COMWDG=%i,\r" ):
    ARDrone2.update( self, cmd )
    if self.loggedVideoResult != None:
      self.lastImageResult = self.loggedVideoResult()


def competeAirRace( drone, desiredSpeed = 0.4, desiredHeight = 1.5, desiredSpeedStep = 0.0 ):
  loops = []
  drone.speed = 0.1
  maxVideoDelay = 0.0
  maxControlGap = 0.0
  estCrossing = None
  try:
    drone.wait(1.0)
    drone.setVideoChannel( front=False )    
    drone.takeoff()
    poseHistory = []
    startTime = drone.time
    while drone.time < startTime + 1.0:
      drone.update("AT*PCMD=%i,0,0,0,0,0\r") # drone.hover(1.0)
      poseHistory.append( (drone.time, (drone.coord[0], drone.coord[1], drone.heading), (drone.angleFB, drone.angleLR)) )
    magnetoOnStart = drone.magneto[:3]
    print "NAVI-ON"
    estCrossing = Pose( drone.coord[0], drone.coord[1], drone.heading ).add( Pose(0.0, CROSSING_Y_COORD, 0.0) ).coord()
    viewlog.dumpBeacon( estCrossing )
    pathType = PATH_TURN_LEFT
    refCircle = None
    refLine = None
    startTime = drone.time
    sx,sy,sz,sa = 0,0,0,0
    lastUpdate = None
    while drone.time < startTime + 600.0:
      sz = max( -0.2, min( 0.2, desiredHeight - drone.coord[2] ))
      sx = max( 0, min( drone.speed, desiredSpeed - drone.vx ))

      if drone.lastImageResult:
        lastUpdate = drone.time
        assert len( drone.lastImageResult ) == 2 and len( drone.lastImageResult[0] ) == 2, drone.lastImageResult
        (frameNumber, timestamp), lastRect = drone.lastImageResult
        viewlog.dumpCamera( "tmp_%04d.jpg" % (frameNumber/15,), 0 )

        if drone.videoHighResolution:
          rects = filterRectangles( lastRect )
        else:
          rects = filterRectangles( lastRect, minWidth=75 )
        cp = classifyPath( [stripPose(r, highResolution=drone.videoHighResolution) for r in rects] )
        if cp != PATH_UNKNOWN:
          if pathType != cp:
            print "TRANS", pathType, "->", cp
            if pathType == PATH_TURN_LEFT and cp == PATH_STRAIGHT:
              loops.append( drone.time )
              desiredSpeed += desiredSpeedStep
              print "SPEED SET TO", desiredSpeed
            if drone.magneto[:3] == magnetoOnStart:
              print "!!!!!!!! COMPASS FAILURE !!!!!!!!"
          pathType = cp
          if pathType == PATH_CROSSING:
            # it is necessary to filter straight segments anyway (i.e. only bad side strip can be detected)
            pathType = PATH_STRAIGHT
        print "FRAME", frameNumber/15, cp, pathType
#        print drone.magneto[12:15]

        # keep history small
        videoTime = correctTimePeriod( timestamp/1000., ref=drone.time )
        videoDelay = drone.time - videoTime
        if videoDelay > 1.0:
          print "!DANGER! - video delay", videoDelay
        maxVideoDelay = max( videoDelay, maxVideoDelay )
        toDel = 0
        for oldTime, oldPose, oldAngles in poseHistory:
          toDel += 1
          if oldTime >= videoTime:
            break
        poseHistory = poseHistory[:toDel]
        if estCrossing:
          dist = distance( oldPose, estCrossing ) - TRANSITION_RADIUS
          if dist < 0:
            if pathType != PATH_STRAIGHT:
              print "NO dist change!", dist
              #pathType = PATH_STRAIGHT
          # TODO force switch to PATH_STRAIGHT for negative value
          # TODO force switch to PATH_TURN_LEFT/RIGHT for positive value based on coordinate, CROSSING_Y_COORD

        for r in rects:
          sPose = Pose( *oldPose ).add( stripPose( r, highResolution=drone.videoHighResolution ) )
          if pathType == PATH_TURN_LEFT:
            circCenter = sPose.add( Pose(0.0, REF_CIRCLE_RADIUS, 0 )).coord()
            viewlog.dumpBeacon( circCenter, index=0 )
            refCircle = circCenter, REF_CIRCLE_RADIUS
          elif pathType == PATH_TURN_RIGHT:
            circCenter = sPose.add( Pose(0.0, -REF_CIRCLE_RADIUS, 0 )).coord()
            viewlog.dumpBeacon( circCenter, index=1 )
            refCircle = circCenter, REF_CIRCLE_RADIUS
          else:
            refCircle = None
          if pathType == PATH_STRAIGHT:
            if refLine == None or abs(normalizeAnglePIPI( refLine.angle - sPose.heading )) < REF_LINE_CROSSING_ANGLE:
              refLine = Line( (sPose.x-0.15*math.cos(sPose.heading), sPose.y-0.15*math.sin(sPose.heading)), 
                                       (sPose.x+0.15*math.cos(sPose.heading), sPose.y+0.15*math.sin(sPose.heading)) )
          else:
            refLine = None
          viewlog.dumpBeacon( sPose.coord(), index=3 )
          viewlog.dumpObstacles( [[(sPose.x-0.15*math.cos(sPose.heading), sPose.y-0.15*math.sin(sPose.heading)), 
                                       (sPose.x+0.15*math.cos(sPose.heading), sPose.y+0.15*math.sin(sPose.heading))]] )

      # error definition ... if you substract that you get desired position or angle
      # error is taken from the path point of view, x-path direction, y-positive left, angle-anticlockwise
      errY, errA = 0.0, 0.0
      assert refCircle == None or refLine == None # they cannot be both active at the same time
      if refCircle:
        if pathType == PATH_TURN_LEFT:
          errY = refCircle[1] - math.hypot( drone.coord[0]-refCircle[0][0], drone.coord[1]-refCircle[0][1] )
          errA = normalizeAnglePIPI( - math.atan2( refCircle[0][1] - drone.coord[1], refCircle[0][0] - drone.coord[0] ) 
                                      - math.radians(-90) + drone.heading )
        if pathType == PATH_TURN_RIGHT:
          errY = math.hypot( drone.coord[0]-refCircle[0][0], drone.coord[1]-refCircle[0][1] ) - refCircle[1]
          errA = normalizeAnglePIPI( math.atan2( refCircle[0][1] - drone.coord[1], refCircle[0][0] - drone.coord[0] ) 
                                      + math.radians(-90) - drone.heading )
      if refLine:
        errY = refLine.signedDistance( drone.coord )
        errA = normalizeAnglePIPI( drone.heading - refLine.angle )

      if refCircle == None and refLine == None:
        sx = 0.0 # wait for Z-up
        if drone.coord[2] > desiredHeight - 0.1:
          print "USING VIRTUAL LEFT TURN CIRCLE!"
          circCenter = Pose( drone.coord[0], drone.coord[1], drone.heading ).add( Pose(0.0, REF_CIRCLE_RADIUS, 0 )).coord()
          viewlog.dumpBeacon( circCenter, index=0 )
          refCircle = circCenter, REF_CIRCLE_RADIUS

      # error correction
      # the goal is to have errY and errA zero in 1 second -> errY defines desired speed at given distance from path
      sy = max( -0.2, min( 0.2, -errY-drone.vy ))/2.0
      
      # there is no drone.va (i.e. derivative of heading) available at the moment ... 
      sa = max( -0.1, min( 0.1, -errA/2.0 ))*1.35

#      print "%0.2f\t%d\t%0.2f\t%0.2f\t%0.2f" % (errY, int(math.degrees(errA)), drone.vy, sy, sa)
      prevTime = drone.time
      drone.moveXYZA( sx, sy, sz, sa )
      maxControlGap = max( drone.time - prevTime, maxControlGap )
      poseHistory.append( (drone.time, (drone.coord[0], drone.coord[1], drone.heading), (drone.angleFB, drone.angleLR)) )
    print "NAVI-OFF", drone.time - startTime
    drone.hover(0.5)
    drone.land()
    drone.setVideoChannel( front=True )    
  except ManualControlException, e:
    print "ManualControlException"
    if drone.ctrlState == 3: # CTRL_FLYING=3 ... i.e. stop the current motion
      drone.hover(0.1)
    drone.land()
  drone.wait(1.0)
  drone.stopVideo()
  print "MaxVideoDelay", maxVideoDelay
  print "MaxControlGap", maxControlGap
  print "Loops in sec", [int(now-prev) for prev,now in zip(loops[:-1],loops[1:])]
  print "Battery", drone.battery


if __name__ == "__main__": 
  import launcher
  launcher.launch( sys.argv, AirRaceDrone, competeAirRace )

