import pygame
import random, math

# When hit by Obstacle, player will lose balls
# Obstacle is the vertical obstacle
# Obstacle2 is a subclass of Obstacle, being the horizontal obstacle
class Obstacle(pygame.sprite.Sprite):
    # a vertical stick that rotates while moving forward
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

    def __init__(self, screenW, screenH, camX, camY, camZ):
        super().__init__()
        # the stick rotates around the center of the screen at random radius
        x = random.randint(100,400)
        self.startX = self.topX = self.bottomX = x
        self.topY = 600
        self.bottomY = 0
        self.startZ = self.topZ = self.bottemZ = 800
        self.i = 0
        self.delta_theta = math.pi / 36
        self.rotate_r = 400 - x
        self.dForward = 10
        self.width = 60
        self.getPos(screenH, camX, camY, camZ)
    
    def doMove(self):
        # rotate the stick
        dx = self.rotate_r - self.rotate_r * math.cos(self.i * self.delta_theta)
        dz = self.rotate_r * math.sin(self.delta_theta) + self.i * self.dForward
        self.topX = self.bottomX = self.startX + dx
        self.topZ = self.bottomZ = self.startZ - dz
    
    def getPos(self, screenH, camX, camY, camZ):
        # get the position on the screen
        self.doMove()
        self.topLeftX, self.topLeftY = Obstacle.transformTo3D(
                                            self.topX - self.width/2,
                                            self.topY, self.topZ,
                                            screenH, camX, camY, camZ)
        self.bottomRtX, self.bottomRtY = Obstacle.transformTo3D(
                                            self.bottomX + self.width/2,
                                            self.bottomY, self.bottomZ,
                                            screenH, camX, camY, camZ)
        self.screenWidth = abs(self.bottomRtX - self.topLeftX)
        self.screenHeight = abs(self.topLeftY - self.bottomRtY)
        # for check collision
        self.rect = pygame.Rect(self.topLeftX,self.topLeftY,
                                self.screenWidth,self.screenHeight)

class Obstacle2(Obstacle):
    # a horizontal stick that moves up and down while moving forward
    def __init__(self, screenW, screenH, camX, camY, camZ):
        self.topX = self.bottomX = screenW / 2
        self.topY = screenH / 2 - 30
        self.bottomY = screenH / 2 + 30
        x = random.randint(100,280)
        self.hiMax = self.bottomY - x
        self.loMax = self.bottomY + x
        self.topZ = self.bottomZ = 800
        self.dForward = 10
        self.width = screenW
        self.direction = 1
        self.dUpDown = self.direction * 10
        self.getPos(screenH, camX, camY, camZ)
    
    def doMove(self):
        self.topZ -= self.dForward
        self.bottomZ -= self.dForward
        if self.bottomY >= self.loMax or self.topY <= self.hiMax:
            self.direction *= -1
        self.dUpDown = self.direction * 10
        self.topY += self.dUpDown
        self.bottomY += self.dUpDown