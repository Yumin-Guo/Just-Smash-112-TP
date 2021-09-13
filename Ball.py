import pygame
# Ball is used to hit other objects
# FakeBall is a subclass of Ball, showing the trajectory
class Ball(pygame.sprite.Sprite):
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
    
    @staticmethod
    def tanToSin(tan_Theta):
        if tan_Theta == 0:
            tan_Theta = 0.01
        tan_Theta_half = ((tan_Theta**2 + 1) - 1) / tan_Theta
        sin_Theta = (2 * tan_Theta_half) / (1 + tan_Theta_half**2)
        return (sin_Theta)

    def __init__(self, aimX, aimY, screenW, screenH, camX, camY, camZ):
        super().__init__()
        originX, originY, originZ = screenW/2, screenH/2, -30
        aimXO = aimX - originX
        aimYO = originY - aimY
        aimZO = min(150 - abs(aimXO)/2.8, 150 - abs(aimYO)/2.8)
        self.v0 = 80
        self.realX, self.realY, self.realZ = screenW / 2, screenH / 2, 0
        self.realR = 36
        self.left = self.realX - self.realR
        self.t = 0
        self.tan_ThetaY_XZ = aimYO / (aimXO**2 + aimZO**2)**.5
        self.sin_ThetaY_XZ = Ball.tanToSin(self.tan_ThetaY_XZ)
        self.cos_ThetaY_XZ = (1 - self.sin_ThetaY_XZ**2)**.5
        if aimXO != 0:
            self.tan_ThetaZ_X = aimZO / aimXO
        else:
            self.tan_ThetaZ_X = aimZO / 0.01
        self.sin_ThetaZ_X = Ball.tanToSin(self.tan_ThetaZ_X)
        self.directionX = self.directionY = 1
        self.bounced = False
        self.getPos(screenW,screenH,camX,camY,camZ)
    
    def changePos(self,screenW, screenH, camX, camY, camZ):
        # movement follows oblique projectile motion
        g = 9.8
        self.dY = self.directionY * self.v0 * self.sin_ThetaY_XZ - g * self.t
        self.dZ = 20
        self.dX = self.dZ / self.tan_ThetaZ_X
        self.realX += self.directionX * self.dX
        self.left += self.directionX * self.dX
        self.realY += self.dY
        self.realZ += self.dZ

    def getPos(self,screenW,screenH,camX,camY,camZ):
        # get screen position
        self.changePos(screenW, screenH, camX, camY, camZ)
        self.screenX,self.screenY=Ball.transformTo3D(
                                    self.realX,self.realY,self.realZ,
                                    screenH,camX,camY,camZ)
        self.leftScreenX = Ball.transformTo3D(self.left,self.realY,self.realZ,
                                                screenH,camX,camY,camZ)[0]
        self.screenR = max(self.screenX - self.leftScreenX,0)
        # for check collision
        self.rect = pygame.Rect(self.leftScreenX, self.screenY-self.screenR,
                                2*self.screenR,2*self.screenR)

class FakeBall(Ball):
    # shown in trajectory
    def __init__(self, aimX, aimY, screenW, screenH, camX, camY, camZ, t):
        self.t = t
        self.overallTime()
        super().__init__(aimX, aimY, screenW, screenH, camX, camY, camZ)
        self.t = t
        self.getPos(screenW,screenH,camX,camY,camZ)
        self.color = (0,0,255-self.realZ//1.8)
    
    def overallTime(self):
        self.overallT = 0
        for i in range(self.t+1):
            self.overallT += i
        
    def changePos(self,screenW, screenH, camX, camY, camZ):
        # instead of change position step by step, change all at once
        super().changePos(screenW, screenH, camX, camY, camZ)
        self.realX, self.realY, self.realZ = screenW / 2, screenH / 2, 0
        self.left = self.realX - self.realR
        g = 9.8
        self.dY = self.directionY * self.v0 * self.sin_ThetaY_XZ * self.t - g * self.overallT
        self.dZ = 20
        self.dX = self.dZ / self.tan_ThetaZ_X
        self.realX += self.directionX * self.dX * self.t
        self.left += self.directionX * self.dX * self.t
        self.realY += self.dY
        self.realZ += self.dZ * self.t