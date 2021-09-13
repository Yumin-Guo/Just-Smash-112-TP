# Name: Yumin Guo 
# Andrew ID: yuming

# template from:
# https://github.com/LBPeraza/Pygame-Asteroids/blob/master/Asteroids/pygamegame.py
# converting 3D to 2D image on screen: 
# https://codeincomplete.com/posts/javascript-racer-v1-straight/
# audio converter:
# https://online-audio-converter.com/
# projectile motion of ball:
# https://baike.baidu.com/item/%E6%96%9C%E6%8A%9B%E8%BF%90%E5%8A%A8

# image of broken glass for main menu:
# http://90sheji.com/sucai/13292326.html
# image of broken glass for game over:
# http://www.51yuansu.com/sc/ercxakcigm.html

# sound effect of breaking glass from: 
# https://freesound.org/people/natemarler/sounds/338692/
# sound effect of vibration from:
# https://freesound.org/people/SOUNDSCAPE_HUMFAK/sounds/258024/
# background music: 
# "yellow" by eel.

# other resources referred to: 
# https://www.pygame.org/docs/index.html
# http://blog.lukasperaza.com/getting-started-with-pygame/
# http://cs.colby.edu/courses/J15/cs369/docs/tutorial01/pygame-tutorial.php
# (adding sound) https://pythonprogramming.net/adding-sounds-music-pygame/
# (reading and writing files) 
# https://www.pythonforbeginners.com/files/reading-and-writing-files-in-python
# (RGB reference) https://blog.csdn.net/daichanglin/article/details/1563299

import pygame
import random, math, string, copy
from Wall import Wall
from Pyramid import Pyramid, BrokenPyramid, Debris
from Ball import Ball, FakeBall
from Obstacle import Obstacle, Obstacle2

class PygameGame(object):
    # the main object where objects interact
    def mousePressed(self, x, y):
        if self.mode == 'main_menu':
            self.mouseMainMenuMode(x,y)
        elif self.mode == 'select_mode':
            self.mouseSelectModeMode(x,y)
        elif self.mode == 'input_name':
            self.mouseInputNameMode(x,y)
        elif self.mode == 'game_ing':
            self.mouseGameMode(x,y)
        elif self.mode == 'game_over':
            self.mouseGameOverMode(x,y)
        elif self.mode == 'score_board':
            self.mouseScoreBoardMode(x,y)

    def mouseGameMode(self,x,y):
        # get the 3d coordinates of mouse click
            (self.realMouseX, self.realMouseY) = x, y
            self.addTrajectory()
    
    def mouseGameOverMode(self,x,y):
        if ( (556 <= x <= 703) and (403 <= y <= 450) ):
            self.mode = 'main_menu'
            self.playerName = ""
        elif ( (556 <= x <= 703) and (464 <= y <= 511) ):
            self.mode = 'score_board'
        else:
            self.mode = 'reset_game'

    def mouseMainMenuMode(self,x,y):
        if ( (537 <= x <= 702) and (320 <= y <= 375) ):
            self.mode = 'select_mode'
        elif ( (537 <= x <= 702) and (412 <= y <= 467) ):
            self.mode = 'instruction1'

    def mouseScoreBoardMode(self,x,y):
        if ( (556 <= x <= 703) and (464 <= y <= 511) ):
            self.mode = 'game_over'
        elif ( (135 <= x <= 283) and (464 <= y <= 511) ):
            self.clearHighScore()

    def mouseInputNameMode(self,x,y):
        if ((297<= x<= 362) and (469<= y<= 513)) and len(self.playerName) > 0:
            self.mode = 'reset_game'
        elif ( (680 <= x <= 745) and (469 <= y <= 513) ):
            self.playerName = ""
            self.mode = 'select_mode'

    def mouseSelectModeMode(self,x,y):
        if ( (412 <= x <= 723) and (263 <= y <= 324) ):
            self.showTrajectory = True
            self.mode = 'input_name'
        elif ( (412 <= x <= 723) and (359 <= y <= 420) ):
            self.showTrajectory = False
            self.mode = 'input_name'

    def mouseReleased(self, x, y):
        if self.mode == 'game_ing':
            # clear the projection
            self.projection = []
            # throw ball
            if self.numBalls > 0:
                self.numBalls -= 1
                self.balls.add(Ball(self.realMouseX, self.realMouseY, 
                                    self.width, self.height, self.camX, 
                                    self.camY, self.camZ))
        elif self.mode == 'reset_game':
            # start the game with 20 balls
            self.generateGame(self.width, self.height)
            self.mode = 'game_ing'
            
    def mouseDrag(self, x, y):
        # update the position of the ball and the trajectory
        if self.mode == 'game_ing':
            (self.realMouseX, self.realMouseY) = x, y
            self.addTrajectory()

    def addTrajectory(self):
        self.projection = []
        # temp projection
        projection = []
        for t in range(20, 0, -1):
            projection.append(FakeBall(self.realMouseX,self.realMouseY,
                                        self.width,self.height,
                                        self.camX,self.camY,self.camZ,t))
        # true projection only with the proper fake balls
        for fakeBall in projection: 
            if (fakeBall.realZ < 800 and 
                fakeBall.realR<fakeBall.realY+fakeBall.realR<self.height and 
                0<fakeBall.realX<self.width):
                self.projection.append(fakeBall)
    
    def testWillCollide(self):
        # predict whether throwing a ball at the moment will hit the pyramid 
        # by checking whether any of the fake balls in projectory will hit
        # the pyramid being moved forward by a certain amount of time
        self.willCollide = False
        for fakeBall in self.projection:
            # check if any of the pyramids will be hit by any of the fake balls
            pyramidFuture = []
            # create a deep copy of complete pyramids
            for pyramid in self.pyramid:
                if not isinstance(pyramid,BrokenPyramid):
                    pyramidFuture.append(Pyramid(pyramid.rlFrtLftX, 
                                                 pyramid.rlFrtLftZ, 
                                                 self.height, self.camX, 
                                                 self.camY, self.camZ))
            for pyramid in pyramidFuture:
                self.movePyramidToPredictedPos(pyramid, fakeBall)
                if ((fakeBall.realZ - fakeBall.realR <= pyramid.rlPeakZ) and 
                    (fakeBall.realX + fakeBall.realR >= pyramid.rlFrtLftX) and 
                    (fakeBall.realX - fakeBall.realR <= pyramid.rlFrtRtX) and
                    (fakeBall.realZ + fakeBall.realR >= pyramid.rlFrtRtZ)):
                    # check collision when almost in the place
                    remove=PygameGame.checkIntersectionPyramid(fakeBall,pyramid)
                    if remove:
                        self.willCollide = True
                        break
            if self.willCollide: break
        for fakeBall in self.projection:
            # update the color to show whether there will be collision
            self.updateTrajectoryColor(fakeBall)

    def movePyramidToPredictedPos(self,pyramid, fakeBall):
        # move pyramids forward by the amount of time indicated by fake ball 
        pyramid.rlFrtLftZ -= pyramid.dZ * (fakeBall.t) * 1.3
        pyramid.rlFrtRtZ -= pyramid.dZ * (fakeBall.t) * 1.3
        pyramid.rlBkLftZ -= pyramid.dZ * (fakeBall.t) * 1.3
        pyramid.rlBkRtZ -= pyramid.dZ * (fakeBall.t) * 1.3
        pyramid.rlPeakZ -= pyramid.dZ * (fakeBall.t) * 1.3

    def updateTrajectoryColor(self,fakeBall):
        if not self.willCollide:
            # blue
            fakeBall.color = (0,0,255-fakeBall.realZ//1.8)
        else:
            # green
            fakeBall.color = (0,255-fakeBall.realZ//1.8,0)

    def keyPressed(self, keyCode, modifier):
        if self.mode in ['instruction1','instruction2','instruction3',
                         'instruction4','instruction5','instruction6',
                         'instruction7']:
            self.instructionKey(keyCode)
        elif self.mode == 'input_name':
            self.getUserName(keyCode,modifier)
        elif self.mode == 'game_ing':
            if keyCode == pygame.K_SPACE:
                # pause the game
                self.setPauseMode()
                self.mode = 'pause'
            elif keyCode == pygame.K_ESCAPE:
                # quick exit, for demo use only
                self.updateHighScore()
                self.mode = 'game_over'
        elif self.mode == 'pause' and keyCode == pygame.K_SPACE:
            # unpause the game
            #pygame.mixer.music.unpause()
            self.mode = 'game_ing'
    
    def setPauseMode(self):
        # when game paused, pause the game and hide the projection and 
        # the text showing gaining or losing of balls (if exist)
        #pygame.mixer.music.pause()
        self.projection = []
        self.hit = self.gain = False

    def getUserName(self,keyCode,modifier):
        if keyCode == pygame.K_BACKSPACE or keyCode == pygame.K_DELETE:
            # delete one character
            self.playerName = self.playerName[:-1]
        else:
            # input the name
            inputChar = pygame.key.name(keyCode)
            if len(self.playerName) < 15:
                if ((inputChar in string.ascii_letters) or 
                    (inputChar in string.digits) or 
                    (inputChar in string.punctuation)):
                    self.playerName += inputChar
        self.textPlayerName()

    def instructionKey(self, keyCode):
        if ((self.mode in ['instruction2','instruction3','instruction4',
                           'instruction5','instruction6','instruction7']) 
            and (keyCode == pygame.K_SPACE)):
            # skip the instruction
            self.mode = 'main_menu'
        elif self.mode == 'instruction1' and keyCode == pygame.K_RIGHT:
            self.mode = 'instruction2'
        elif self.mode == 'instruction2':
            if keyCode == pygame.K_RIGHT: self.mode = 'instruction3'
            elif keyCode == pygame.K_LEFT: self.mode = 'instruction1'
        elif self.mode == 'instruction3':
            if keyCode == pygame.K_RIGHT: self.mode = 'instruction4'
            elif keyCode == pygame.K_LEFT: self.mode = 'instruction2'
        elif self.mode == 'instruction4':
            if keyCode == pygame.K_RIGHT: self.mode = 'instruction5'
            elif keyCode == pygame.K_LEFT: self.mode = 'instruction3'
        elif self.mode == 'instruction5':
            if keyCode == pygame.K_RIGHT: self.mode = 'instruction6'
            elif keyCode == pygame.K_LEFT: self.mode = 'instruction4'
        elif self.mode == 'instruction6':
            if keyCode == pygame.K_RIGHT: self.mode = 'instruction7'
            elif keyCode == pygame.K_LEFT: self.mode = 'instruction5'
        elif self.mode == 'instruction7' and keyCode == pygame.K_LEFT:
            self.mode = 'instruction6'

    def keyReleased(self, keyCode, modifier):
        pass

    def timerFired(self, dt):
        # update the text
        self.textNumBalls()
        self.textDistanceTraveled()
        self.textPlayerName()
        self.textTopScore()
        if self.mode == 'game_ing':
            self.timeCountAppear += dt
            self.timeCountMove += dt
            # update color of the trajectory
            self.testWillCollide()
            if self.timeCountAppear >= 2000:
                self.timeCountAppear = 0
                self.gameOverTimeCount = 0
                self.addPyramidOrObstacle()
            if self.timeCountMove >= 10:
                self.timeCountMove = 0
                self.distanceTraveled += 1
                self.actionPerUnitTime()
    
    def addPyramidOrObstacle(self):
        # farther distance travelled, fewer pyramid and more obstacle
        if self.distanceTraveled < 300 and self.pyramidtimeCount % 5 != 0:
            # add pyramid
            self.generatePyramid()
        elif 300< self.distanceTraveled < 600 and self.pyramidtimeCount %4 != 0:
            # add pyramid
            self.generatePyramid()
        elif self.distanceTraveled > 600 and self.pyramidtimeCount % 3 != 0:
            # add pyramid
            self.generatePyramid()
        else:
            # add obstacle
            for _ in range(min(1 + self.distanceTraveled//300,4)):
                self.obstacle.add(random.choice(
                    [Obstacle(self.width, self.height, 
                              self.camX, self.camY, self.camZ),
                     Obstacle2(self.width, self.height, 
                               self.camX, self.camY, self.camZ)]))
            self.pyramidtimeCount += 1

    def actionPerUnitTime(self):
        if self.hit:
            # remain the state for some time to show wall color change and text
            self.hitCount += 1
            if self.hitCount % 8 == 0:
                self.hit = False
        if self.gain:
            # remain the state for some time to display text
            self.gainCount += 1
            if self.gainCount % 8 == 0:
                self.gain = False
        # add a new level of wall to the screen if currently full screen
        (beginDep,endDep) = (790, self.numWall * self.wallThickness)
        if len(self.wall) == 10:
            self.generateWall(beginDep, endDep)
        # move all the objects
        self.moveWall()
        self.movePyramids()
        self.moveDebris()
        self.moveBall()
        self.moveObstacle()
        if self.numBalls <= 0:
            # leave time to see if the last ball thrown hit the pyramid 
            # (which will add numBalls). If not, game over
            self.gameOverTimeCount += 1
            if self.gameOverTimeCount >= 10:
                self.updateHighScore()
                self.mode = 'game_over'
    
    def updateHighScore(self):
        for i in range(5):
            # loop through the score list to see if the new score will be added
            score = self.topScore[i]
            if ((score == "-") or (self.distanceTraveled >= int(score))):
                self.topScore.insert(i,self.distanceTraveled)
                self.winner.insert(i,self.playerName)
                self.topScore.pop()
                self.winner.pop()
                break
        # edit the score text file
        file = open("highest scores.txt","w")
        file.write(f'{self.winner[0]}:{self.topScore[0]}\n')
        file.write(f'{self.winner[1]}:{self.topScore[1]}\n')
        file.write(f'{self.winner[2]}:{self.topScore[2]}\n')
        file.write(f'{self.winner[3]}:{self.topScore[3]}\n')
        file.write(f'{self.winner[4]}:{self.topScore[4]}\n')
        file.close()
    
    def clearHighScore(self):
        # clear the score text file to original state
        self.winner = ["-"] * 5
        self.topScore = ["-"] * 5
        file = open("highest scores.txt","w")
        file.write(f'{self.winner[0]}:{self.topScore[0]}\n')
        file.write(f'{self.winner[1]}:{self.topScore[1]}\n')
        file.write(f'{self.winner[2]}:{self.topScore[2]}\n')
        file.write(f'{self.winner[3]}:{self.topScore[3]}\n')
        file.write(f'{self.winner[4]}:{self.topScore[4]}\n')
        file.close()

    def moveObstacle(self):
        # move the obstacle on its path
        allObstacle = set()
        for obstacle in self.obstacle:
            if type(obstacle) == Obstacle:
                obstacle.i += 1
            # obstacle.dForward = 10 * (1 + self.distanceTraveled // 30)
            obstacle.getPos(self.height, self.camX, self.camY, self.camZ)
            if obstacle.topZ > -30:
                allObstacle.add(obstacle)
            else:
                # if get to the Z position of the ball, get hit if 
                # its X/Y position is also close to the X/Y position of camera
                if (type(obstacle) == Obstacle):
                    # verticle stick
                    if ((350<=obstacle.topX<=450) or 
                        (320<=obstacle.bottomX<=480)):
                        self.numBalls -= 5
                        self.hit = True
                        self.hitCount += 1
                        pygame.mixer.Sound.play(self.crash_stick)
                else:
                    # Obstacle2: horizontal stick
                    if (200<=obstacle.topY<=400):
                        self.numBalls -= 5
                        self.hit = True
                        self.hitCount += 1
                        pygame.mixer.Sound.play(self.crash_stick)
        self.obstacle = allObstacle
    
    def moveWall(self):
        # move the wall, remove it if go off screen, 
        # then change color for all the walls
        walls = set()
        noRemove = True
        for wall in self.wall:
            if wall.endDep-wall.beginDep == self.wallThickness:
                wall.endDep -= 10
            wall.beginDep -=10
            wall.colorChange = self.hit
            wall.getScreenPos(self.width,self.height,
                                self.camX,self.camY,self.camZ)
            if wall.endDep > 0: 
                walls.add(wall)
        self.wall = walls

    def moveDebris(self):
        # move the pyramid debris forward
        newDebris = []
        for debris in self.debris:
            debris.rlFrtLftZ -= debris.dZ
            debris.rlFrtRtZ -= debris.dZ
            debris.rlBkRtZ -= debris.dZ
            debris.rlBkLftZ -= debris.dZ
            debris.rlPeakZ -= debris.dZ
            debris.getPositionScreen(self.height,self.camX,self.camY,self.camZ)
            if debris.rlBkLftZ > 0:
                newDebris.append(debris)
        self.debris = newDebris

    def movePyramids(self):
        # move the pyramids forward
        newPyramids = []
        for pyramid in self.pyramid:
            pyramid.rlFrtLftZ -= pyramid.dZ
            pyramid.rlFrtRtZ -= pyramid.dZ
            pyramid.rlBkRtZ -= pyramid.dZ
            pyramid.rlBkLftZ -= pyramid.dZ
            pyramid.rlPeakZ -= pyramid.dZ
            if isinstance(pyramid,BrokenPyramid):
                pyramid.rlBreakFrtZ -= pyramid.dZ
                pyramid.rlBreakMidZ -= pyramid.dZ
                pyramid.rlBreakBkZ -= pyramid.dZ
            pyramid.getPositionScreen(self.height,self.camX,
                                        self.camY,self.camZ)
            # if goes off screen, remove from the set
            if pyramid.rlBkLftZ > 0:
                newPyramids.append(pyramid)
        self.pyramid = newPyramids
    
    def moveBall(self):
        newBalls = set()
        for balls in self.balls:
            balls.t += 1
            balls.getPos(self.width,self.height,self.camX,self.camY,self.camZ)
            if balls.realZ <= 800 and balls.realY > 0:
                # if the ball has not bounced even once, and it reaches 
                # the edge, move in the opposite direction
                if ((balls.realX < 0 or balls.realX > self.width) 
                    and (not balls.bounced)):
                    balls.bounced = True
                    balls.directionX *= -1
                elif ((balls.realY > self.height) and (not balls.bounced)):
                    balls.bounced = True
                    balls.directionY *= -1
                newBalls.add(balls)
        self.balls = newBalls
        self.checkCollidePyramid()
        self.checkCollideStick()

    @staticmethod
    def checkIntersection(k, b, xO, yO, r):
        # check collision between line: y=kx+b & circle: (x-xO)^2+(y-yO)^2=r^2
        # transform the equation and get the function: 
        # (k^2+1)*x^2 + 2(bk-yOk-xO)*x + xO^2+yO^2+b^2-2bYO-r^2 = 0
        delta = (( 2 * ( b * k - yO * k - xO ))**2 - 4 * ( k**2 + 1 ) * 
                    ( xO**2 + yO**2 + b**2 - 2 * b * yO - r**2 ))
        return delta >= 0
    
    @staticmethod
    def checkIntersectionPyramid(ball, prism):
        # line: y = x * (PeakY-rlBottomY) / (PeakZ-rlFrtRtZ) + rlBottomY 
        #           - (PeakY-rlBottomY) / (PeakZ-rlFrtRtZ )
        # circle: (x-realZ)**2 + (y-realY)**2 = realR**2
        k = (prism.h - prism.rlBottomY) / (prism.rlPeakZ - prism.rlBottomY)
        b = prism.rlBottomY - k * prism.rlFrtRtZ
        xO = ball.realZ
        yO = ball.realY
        r = ball.realR
        return PygameGame.checkIntersection(k, b, xO, yO, r)

    def checkCollidePyramid(self):
        # check if ball collide with pyramid
        for ball in self.balls:
            newPyramids = []
            for pyramid in self.pyramid:
                remove = False
                if not isinstance(pyramid,BrokenPyramid):
                    # Broken pyramid cannot be broken again
                    if ((ball.realZ - ball.realR <= pyramid.rlPeakZ) and 
                        (ball.realX + ball.realR >= pyramid.rlFrtLftX) and 
                        (ball.realX - ball.realR <= pyramid.rlFrtRtX) and
                        (ball.realZ + ball.realR >= pyramid.rlFrtRtZ)):
                        # check collision when almost in the place
                        remove=PygameGame.checkIntersectionPyramid(ball,pyramid)
                        if remove:
                            # play sound effect
                            pygame.mixer.Sound.play(self.crash_pyramid)
                            self.gain = True
                            self.gainCount += 1
                            self.numBalls += 2
                            newPyramids.append(
                                BrokenPyramid(pyramid.rlFrtLftX, 
                                              pyramid.rlFrtLftZ, 
                                              self.height, self.camX, 
                                              self.camY, self.camZ))
                            self.addDebris(pyramid)
                if not remove:
                    newPyramids.append(pyramid)
            self.pyramid = newPyramids
    
    def addDebris(self,pyramid):
        # randomly decide the number of debris drawn on each side of pyramid
        leftNum = random.randint(3,9)
        for _ in range (leftNum):
            length = random.randint(2,10)
            leftMost = max(0,pyramid.rlFrtLftX-30)
            rlFrtLftX = random.randint(leftMost, pyramid.rlFrtLftX)
            backMost = pyramid.rlFrtLftZ+pyramid.length
            rlFrtLftZ = random.randint(pyramid.rlFrtLftZ, backMost)
            self.debris.append(Debris(rlFrtLftX, rlFrtLftZ, self.height, 
                                      self.camX, self.camY, self.camZ,length))
        for _ in range (12-leftNum):
            length = random.randint(2,10)
            rightMost = min(pyramid.rlFrtRtX+30,self.width-10)
            rlFrtLftX = random.randint(pyramid.rlFrtRtX, rightMost)
            backMost = pyramid.rlFrtLftZ+pyramid.length
            rlFrtLftZ = random.randint(pyramid.rlFrtLftZ, backMost)
            self.debris.append(Debris(rlFrtLftX, rlFrtLftZ, self.height, 
                                      self.camX, self.camY, self.camZ,length))

    def checkCollideStick(self):
        # check if ball collide with sticks
        for balls in self.balls:
            newObstacle = set()
            for obstacle in self.obstacle:
                removeObstacle = False
                if (balls.realZ-balls.realR <= 
                    obstacle.topZ <= balls.realZ+balls.realR):
                    # when almost in place, check collision as sprite
                    removeObstacle = pygame.sprite.collide_rect(balls, obstacle)
                if not removeObstacle:
                    newObstacle.add(obstacle)
            self.obstacle = newObstacle


    def drawWall(self,screen):
        # draw walls based on their color
        for wall in self.wall:
            pygame.draw.polygon(screen,wall.upDownColor,wall.upWall)
            pygame.draw.polygon(screen,wall.leftRightColor,wall.leftWall)
            pygame.draw.polygon(screen,wall.upDownColor,wall.downWall)
            pygame.draw.polygon(screen,wall.leftRightColor,wall.rightWall)

    def drawPyramid(self,screen):
        for pyramid in self.pyramid:
            if not isinstance(pyramid, BrokenPyramid):
                self.drawCompletePyramid(screen,pyramid)
            else:
                self.drawBrokenPyramid(screen,pyramid)

    def drawCompletePyramid(self,screen,pyramid):
        basePos = (pyramid.posScreen[0],pyramid.posScreen[1],
                        pyramid.posScreen[2],pyramid.posScreen[3])
        backPos = (pyramid.posScreen[2], pyramid.posScreen[3], 
                        pyramid.posScreen[4])
        leftPos = (pyramid.posScreen[0], pyramid.posScreen[3], 
                        pyramid.posScreen[4])
        rightPos = (pyramid.posScreen[1], pyramid.posScreen[2], 
                            pyramid.posScreen[4])
        frontPos = (pyramid.posScreen[0], pyramid.posScreen[1], 
                            pyramid.posScreen[4])
        # order of drawing depends on position so that looks 3D
        if pyramid.rlFrtLftX > self.camX:
            pyramidPosition=[basePos, backPos, rightPos, leftPos, frontPos]
        else:
            pyramidPosition=[basePos, backPos, leftPos, rightPos, frontPos]
        for positions in pyramidPosition:
            pygame.draw.polygon(screen,(215,245,245),positions)
            pygame.draw.polygon(screen,(0,0,205),positions,1)

    def drawBrokenPyramid(self,screen,pyramid):
        basePos = (pyramid.posScreen[5],pyramid.posScreen[6],
                pyramid.posScreen[8],pyramid.posScreen[7])
        backPos = (pyramid.posScreen[3],pyramid.posScreen[4],
                pyramid.posScreen[8],pyramid.posScreen[7])
        leftPos = (pyramid.posScreen[0],pyramid.posScreen[3],
                pyramid.posScreen[7],pyramid.posScreen[5])
        rightPos = (pyramid.posScreen[2],pyramid.posScreen[4],
                    pyramid.posScreen[8],pyramid.posScreen[6])
        innerPos = (pyramid.posScreen[0],pyramid.posScreen[1],
                    pyramid.posScreen[2],pyramid.posScreen[4],
                    pyramid.posScreen[3])
        frontPos = (pyramid.posScreen[0],pyramid.posScreen[1],
                    pyramid.posScreen[2],pyramid.posScreen[6],
                    pyramid.posScreen[5])
        # order of drawing depends on position so that looks 3D
        if pyramid.rlFrtLftX > self.camX:
            pyramidPosition=[basePos,backPos,rightPos,leftPos,innerPos,frontPos]
        else:
            pyramidPosition=[basePos,backPos,leftPos,rightPos,innerPos,frontPos]
        for positions in pyramidPosition:
            pygame.draw.polygon(screen,(215,245,245),positions)
            pygame.draw.polygon(screen,(0,0,205),positions,1)

    def drawDebris(self,screen):
        for debris in self.debris:
            self.drawCompletePyramid(screen,debris)

    def drawObstacle(self,screen):
        for obstacle in self.obstacle:
            pygame.draw.rect(screen, (200-obstacle.topZ//10,0,0),
                             (obstacle.topLeftX, obstacle.topLeftY, 
                             obstacle.screenWidth, obstacle.screenHeight))
            pygame.draw.rect(screen, (20,0,0),
                             (obstacle.topLeftX, obstacle.topLeftY, 
                             obstacle.screenWidth, obstacle.screenHeight),1)

    def drawBall(self,screen):
        for balls in self.balls:
            pygame.draw.circle(screen,(0,20,0),(int(balls.screenX), 
                               int(balls.screenY)), int(balls.screenR))
            pygame.draw.circle(screen,(0,0,0),(int(balls.screenX), 
                               int(balls.screenY)), int(balls.screenR),1)
            # two more circles as if light on the ball to make it more 3D
            pygame.draw.circle(screen,(10,50,10),
                               (int(balls.screenX-3*balls.screenR/8), 
                                int(balls.screenY-3*balls.screenR/8)), 
                               int(balls.screenR/3))
            pygame.draw.circle(screen,(20,80,20),
                               (int(balls.screenX-4*balls.screenR/8), 
                                int(balls.screenY-4*balls.screenR/8)), 
                               int(balls.screenR/6))

    def drawTrajectory(self,screen):
        if self.showTrajectory:
            for i in range(0,len(self.projection),2):
                # draw half of the fake balls in trajectory to look clearer
                balls = self.projection[i]
                pygame.draw.circle(screen,balls.color,(int(balls.screenX), 
                                   int(balls.screenY)), int(balls.screenR))

    def drawLoseBall(self,screen):
        screen.blit(self.textLose,(550,50))
    
    def drawGainBall(self,screen):
        screen.blit(self.textGain, (550,50))

    def drawGameMode(self,screen):
        self.drawWall(screen)
        self.drawDebris(screen)
        self.drawPyramid(screen)
        self.drawObstacle(screen)
        self.drawBall(screen)
        self.drawTrajectory(screen)
        screen.blit(self.text1, (300, 50))
        screen.blit(self.textDist,(50,50))
        if self.hit:
            self.drawLoseBall(screen)
        if self.gain:
            self.drawGainBall(screen)

    def drawPauseMode(self,screen):
        self.drawGameMode(screen)
        screen.blit(self.textToUnpause, (240, 150))
        screen.blit(self.pauseSign,(250,300))

    def drawGameOver(self,screen):
        screen.blit(self.gameOverImage,(0,0))
        screen.blit(self.text2, (240,300))

    def drawMainMenu(self,screen):
        screen.blit(self.mainMenu,(0,0))

    def drawInstruction(self,screen):
        if self.mode == 'instruction1':
            screen.blit(self.instruct1,(0,0))
        elif self.mode == 'instruction2':
            screen.blit(self.instruct2,(0,0))
        elif self.mode == 'instruction3':
            screen.blit(self.instruct3,(0,0))
        elif self.mode == 'instruction4':
            screen.blit(self.instruct4,(0,0))
        elif self.mode == 'instruction5':
            screen.blit(self.instruct5,(0,0))
        elif self.mode == 'instruction6':
            screen.blit(self.instruct6,(0,0))
        elif self.mode == 'instruction7':
            screen.blit(self.instruct7,(0,0))

    def drawNameInput(self,screen):
        screen.blit(self.nameInput,(0,0))
        screen.blit(self.textName,(81,432))

    def drawScoreBoard(self,screen):
        screen.blit(self.scoreBoard,(0,0))
        screen.blit(self.scoreL1,(240,200))
        screen.blit(self.scoreL2,(240,250))
        screen.blit(self.scoreL3,(240,300))
        screen.blit(self.scoreL4,(240,350))
        screen.blit(self.scoreL5,(240,400))
    
    def drawSelectMode(self,screen):
        screen.blit(self.select_mode, (0,0))

    def redrawAll(self, screen):
        if self.mode == 'main_menu':
            self.drawMainMenu(screen)
        elif self.mode in ['instruction1','instruction2','instruction3',
                           'instruction4','instruction5','instruction6',
                           'instruction7']:
            self.drawInstruction(screen)
        elif self.mode == 'select_mode':
            self.drawSelectMode(screen)
        elif self.mode == 'input_name':
            self.drawNameInput(screen)
        if self.mode == 'game_ing':
            self.drawGameMode(screen)
            screen.blit(self.textToPause, (50,10))
        elif self.mode == 'pause':
            self.drawPauseMode(screen)
        elif self.mode == 'game_over':
            self.drawGameOver(screen)
        elif self.mode == 'score_board':
            self.drawScoreBoard(screen)

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)
    
    def textNumBalls(self):
        # create a font
        theFont = pygame.font.SysFont( "Helvetica", 40, bold=True )
        # render a surface with some text
        self.text1 = theFont.render( f"{max(self.numBalls,0)} balls left", 
                                     True, (255, 200, 255) )

    def textLoseBall(self):
        theFont = pygame.font.SysFont( "Helvetica", 40, bold=False )
        self.textLose = theFont.render( "- 5", True, (200, 200, 0) )

    def textGainBall(self):
        theFont = pygame.font.SysFont( "Helvetica", 40, bold=False )
        self.textGain = theFont.render( "+ 2", True, (220, 220, 0) )

    def textPlayerName(self):
        theFont = pygame.font.SysFont( "Helvetica", 30, bold=False )
        self.textName = theFont.render( f"{self.playerName}", 
                                    True, (240, 240, 240) )

    def textDistanceTraveled(self):
        theFont = pygame.font.SysFont( "Helvetica", 30, bold=False )
        self.text2 = theFont.render( f"You have travelled {self.distanceTraveled} m", 
                                    True, (240, 240, 240) )
        theFont1 = pygame.font.SysFont( "Helvetica", 30, bold=False )
        self.textDist = theFont1.render( f"Distance: {self.distanceTraveled} m", 
                                    True, (240, 240, 240) )

    def textPause(self):
        theFont = pygame.font.SysFont( "Helvetica", 30, bold=False )
        self.textToPause = theFont.render( "press SPACE to pause the game", 
                                    True, (240, 240, 240) )
        self.textToUnpause = theFont.render( "press SPACE to continue",
                                    True, (240, 240, 240) )

    def textTopScore(self):
        self.getHighestScore()
        theFont = pygame.font.SysFont( "Helvetica", 30, bold=False )
        self.scoreL1 = theFont.render( f"1st: {self.winner[0]}: {self.topScore[0]}", 
                                    True, (240, 240, 240) )
        self.scoreL2 = theFont.render( f"2nd: {self.winner[1]}: {self.topScore[1]}", 
                                    True, (240, 240, 240) )
        self.scoreL3 = theFont.render( f"3rd: {self.winner[2]}: {self.topScore[2]}", 
                                    True, (240, 240, 240) )
        self.scoreL4 = theFont.render( f"4th: {self.winner[3]}: {self.topScore[3]}", 
                                    True, (240, 240, 240) )
        self.scoreL5 = theFont.render( f"5th: {self.winner[4]}: {self.topScore[4]}", 
                                    True, (240, 240, 240) )

    def generateText(self):
        self.textDistanceTraveled()
        self.textNumBalls()
        self.textGainBall()
        self.textLoseBall()
        self.textPause()

    def generatePics(self):
        self.generateMainMenu()
        self.generateInstruction()
        self.generateNameInput()
        self.generateSelectMode()
        self.generateGameOver()
        self.generateScoreBoard()
        self.generatePause()

    def generateMainMenu(self):
        self.mainMenu = pygame.transform.scale(
            pygame.image.load("broken glass duplicate.png"),(800,600))
    
    def generateInstruction(self):
        self.instruct1 = pygame.transform.scale(
            pygame.image.load("Instruction1.png"),(800,600))
        self.instruct2 = pygame.transform.scale(
            pygame.image.load("Instruction2.png"),(800,600))
        self.instruct3 = pygame.transform.scale(
            pygame.image.load("Instruction3.png"),(800,600))
        self.instruct4 = pygame.transform.scale(
            pygame.image.load("Instruction4.png"),(800,600))
        self.instruct5 = pygame.transform.scale(
            pygame.image.load("Instruction5.png"),(800,600))
        self.instruct6 = pygame.transform.scale(
            pygame.image.load("Instruction6.png"),(800,600))
        self.instruct7 = pygame.transform.scale(
            pygame.image.load("Instruction7.png"),(800,600))

    def generateNameInput(self):
        self.nameInput = pygame.transform.scale(
            pygame.image.load("input name.png"),(800,600))

    def generateSelectMode(self):
        self.select_mode = pygame.transform.scale(
            pygame.image.load("select_mode.png"),(800,600))

    def generateGameOver(self):
        self.gameOverImage = pygame.transform.scale(
            pygame.image.load("Game_Over.png"),(800,600))

    def generateScoreBoard(self):
        self.textTopScore()
        self.scoreBoard = pygame.transform.scale(
            pygame.image.load("Top_Score.png"),(800,600))

    def generatePause(self):
        self.pauseSign = pygame.transform.scale(
            pygame.image.load("pause_sign.png"),(300,300))

    def generateWall(self, beginDep, endDep):
        self.wall.add(Wall(beginDep, self.width, self.height,
                            self.camX,self.camY,self.camZ))
    
    def generatePyramid(self):
        self.pyramidtimeCount += 1
        # generate a pyramid from end of the road at random X
        realFrtLeftX = random.randint(100,self.width - 100)
        realFrtLeftZ = 750
        # insert to the index0 of the list so that drawn at the back
        self.pyramid.insert(0,Pyramid(realFrtLeftX, realFrtLeftZ, self.height, 
                                 self.camX, self.camY, self.camZ))

    def generateGame(self, width, height):
        # basic setting
        self.bgColor = (200, 250, 200)
        self.distanceTraveled = 0
        self.camX, self.camY, self.camZ = width/2, height/2, -100
        # generate walls
        self.wall = set()
        self.wallThickness = 80
        self.numWall = 10
        for i in range(self.numWall):
            (beginDep,endDep)=(i* self.wallThickness,(i+1)* self.wallThickness)
            self.generateWall(beginDep, endDep)
        # generate pyramid
        self.pyramid = []
        self.pyramidtimeCount = 0
        self.generatePyramid()
        self.debris = []
        # place for balls
        self.balls = set()
        self.numBalls = 20
        # place for projection
        self.projection = []
        self.willCollide = False
        # place for obstacles
        self.obstacle = set()
        # other
        self.timeCountAppear = self.timeCountMove = 0
        self.gain = False
        self.gainCount = 0
        self.hit = False
        self.hitCount = 0
        # reset game over features
        self.gameOverTimeCount = 0

    def getHighestScore(self):
        file = open("highest scores.txt", "r")
        self.winner = []
        self.topScore = []
        for line in file:
            temp = []
            for word in line.split(":"):
                temp.append(word)
            self.winner.append(temp[0])
            self.topScore.append(temp[1].strip())
        file.close()

    def __init__(self, width=800, height=600, fps=100, title="Just Smash!"):
        pygame.font.init()
        pygame.init()
        # set the background music
        pygame.mixer.music.load('eel. - yellow.wav')
        pygame.mixer.music.play(-1)
        self.crash_pyramid = pygame.mixer.Sound('glass-break-small.wav')
        self.crash_stick = pygame.mixer.Sound('vibrating_alert.wav')
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.mode = 'main_menu'
        self.generatePics()
        self.generateGame(width, height)
        self.generateText()
        self.playerName = ""
        self.showTrajectory = True
        
    
    def run(self):

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        
        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        # self.init()
        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    playing = False
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.update()

        pygame.quit()


def main():
    game = PygameGame()
    game.run()

if __name__ == '__main__':
    main()