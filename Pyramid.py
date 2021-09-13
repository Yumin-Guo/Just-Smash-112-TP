# Pyramid is the one object being hit to win more balls
# BrokenPyramid is subclass of Pyramid, the pyramid after being hit by the ball
# Debris is subclass of Pyramid, the debris of the pyramid after being hit. 
# It has the same shape as pyramid, but with smaller size

class Pyramid(object):
    # the main pyramid shown on the screen
    @staticmethod
    def transformTo3D(worldX,worldY,worldZ,screenH,camX,camY,camZ):
        # transform a 3D point into a pair of 2D coordinates
        XToCam, YToCam = worldX-camX, worldY-camY
        ZToCam = worldZ-camZ
        XProject = (abs(camZ) * XToCam) / ZToCam
        YProject = (abs(camZ) * YToCam) / ZToCam
        XScreen = camX + XProject
        YScreen = screenH - YProject - camY
        return (XScreen, YScreen)

    def __init__(self,rlFrtLftX, rlFrtLftZ, screenH, camX, camY, camZ):
        # define the real 3d position based on front-left corner of pyramid
        if not isinstance(self,Debris):
            self.length = 50
        self.rlFrtLftX = self.rlBkLftX = rlFrtLftX
        self.rlFrtLftZ = self.rlFrtRtZ = rlFrtLftZ
        self.rlFrtRtX = self.rlBkRtX = self.rlFrtLftX + self.length
        self.rlBkLftZ = self.rlBkRtZ = self.rlFrtLftZ + self.length
        self.rlBottomY = 0
        self.h = 4 * self.length
        self.rlPeakX = self.rlFrtLftX + self.length / 2
        self.rlPeakZ = self.rlBkLftZ - self.length / 2
        self.dZ = 10
        if type(self) == Pyramid:
            self.getPositionScreen(screenH, camX, camY, camZ)

    def getPositionReal(self):
        # put real world positions into list
        self.positionRl=[(self.rlFrtLftX,self.rlBottomY,self.rlFrtLftZ),
                         (self.rlFrtRtX, self.rlBottomY,self.rlFrtRtZ),
                         (self.rlBkRtX,  self.rlBottomY,self.rlBkRtZ),
                         (self.rlBkLftX, self.rlBottomY,self.rlBkLftZ),
                         (self.rlPeakX,  self.h,        self.rlPeakZ)]

    def getPositionScreen(self, screenH, camX, camY, camZ):
        # transform real world position list to screen 2d list
        self.getPositionReal()
        self.posScreen = []
        for point in self.positionRl:
            pointX, pointY, pointZ = point
            screenPos = Pyramid.transformTo3D(pointX, pointY, pointZ, screenH, 
                                      camX, camY, camZ)
            self.posScreen.append(screenPos)

class BrokenPyramid(Pyramid):
    # pyramid after being broken
    def __init__(self,rlFrtLftX, rlFrtLftZ, screenH, camX, camY, camZ):
        super().__init__(rlFrtLftX, rlFrtLftZ, screenH, camX, camY, camZ)
        self.rlBreakLftX = self.rlFrtLftX + self.length / 4
        self.rlBreakRtX = self.rlFrtRtX - self.length / 4
        self.rlBreakY = self.h / 2
        self.rlBreakFrtZ = (self.rlFrtLftZ+self.rlPeakZ)/2
        self.rlBreakBkZ = (self.rlBkLftZ+self.rlPeakZ)/2
        self.rlBreakMidX = self.rlPeakX
        self.rlBreakMidY = self.h / 3
        self.rlBreakMidZ = 2 * self.rlFrtLftZ / 3 + self.rlPeakZ / 3
        self.getPositionScreen(screenH, camX, camY, camZ)

    def getPositionReal(self):
        # put real world positions into list
        self.positionRl=[(self.rlBreakLftX, self.rlBreakY, self.rlBreakFrtZ),
                        (self.rlBreakMidX, self.rlBreakMidY, self.rlBreakMidZ),
                        (self.rlBreakRtX,  self.rlBreakY,  self.rlBreakFrtZ),
                        (self.rlBreakLftX, self.rlBreakY, self.rlBreakBkZ),
                        (self.rlBreakRtX, self.rlBreakY, self.rlBreakBkZ),
                        (self.rlFrtLftX,self.rlBottomY,self.rlFrtLftZ),
                        (self.rlFrtRtX, self.rlBottomY,self.rlFrtRtZ),
                        (self.rlBkLftX, self.rlBottomY,self.rlBkLftZ),
                        (self.rlBkRtX,  self.rlBottomY,self.rlBkRtZ)]

class Debris(Pyramid):
    # the debris are shown as tiny pyramids
    def __init__(self,rlFrtLftX, rlFrtLftZ, screenH, camX, camY, camZ,length):
        self.length = length
        super().__init__(rlFrtLftX, rlFrtLftZ, screenH, camX, camY, camZ)
        self.getPositionScreen(screenH, camX, camY, camZ)