# Wall is the overall setting of the game

class Wall(object):
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

    # the background
    def __init__(self, beginDep, screenW, screenH,camX,camY,camZ):
        self.beginDep = beginDep
        self.thick = 80
        self.endDep = self.beginDep + self.thick
        self.colorChange = False
        self.getScreenPos(screenW,screenH,camX,camY,camZ)

    def getRealPos(self, screenW, screenH):
        # get the position of all coordinates in real world for each wall
        realTopLftOut = (0,screenH,self.beginDep)
        realTopRtOut = (screenW,screenH,self.beginDep)
        realBtmRtOut = (screenW,0,self.beginDep)
        realBtmLftOut = (0,0,self.beginDep)
        realTopLftIn = (0,screenH,self.endDep)
        realTopRtIn = (screenW,screenH,self.endDep)
        realBtmRtIn = (screenW,0,self.endDep)
        realBtmLftIn = (0,0,self.endDep)
        self.realPosList = [realTopLftOut, realTopRtOut, realBtmRtOut, 
                            realBtmLftOut, realTopLftIn, realTopRtIn, 
                            realBtmRtIn, realBtmLftIn]
        
    def getScreenPos(self,screenW,screenH,camX,camY,camZ):
        # transform the positions to the screen
        self.getRealPos(screenW, screenH)
        screenPos = []
        for point in self.realPosList:
            realX,realY,realZ = point
            onScreen = Wall.transformTo3D(realX, realY, realZ,
                                          screenH, camX, camY, camZ)
            screenPos.append(onScreen)
        self.upWall = (screenPos[0],screenPos[1],screenPos[5],screenPos[4])
        self.downWall = (screenPos[2],screenPos[3],screenPos[7],screenPos[6])
        self.leftWall = (screenPos[0],screenPos[4],screenPos[7],screenPos[3])
        self.rightWall = (screenPos[1],screenPos[5],screenPos[6],screenPos[2])
        # color changes based on level
        self.level = (self.beginDep + self.endDep + self.thick) / 2 / self.thick
        self.getColor()
    
    def getColor(self):
        # the closer to the screen, the deeper the color
        if self.colorChange:
            # color of the wall when being hit
            self.upDownColor = (30+20*self.level,self.level*8,self.level*8)
            self.leftRightColor = (40+20*self.level,self.level*8,self.level*8)
        else:
            # normal color of wall
            self.upDownColor = (self.level*18,30+20*self.level,self.level*18)
            self.leftRightColor = (self.level*18,40+20*self.level,self.level*18)