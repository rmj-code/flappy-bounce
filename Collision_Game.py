

import pygame
import random
import os
import time
import neat

WIN_WIDTH = 600
WIN_HEIGHT = 700
FLOOR_HEIGHT = 650

START_VEL = 10.5
FRICTION = 0.94

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)


win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Bounce")

# pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
pipe_img = pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha()
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())


class Ball:
	IMGS = bird_images
	ANIMATION_TIME = 5

	def  __init__(self, x, y):
		self.x = x
		self.y = y

		self.has_collided = False	# Flag for whether ball has hit ground or not

		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0 			# for keepting track of which ball image is being used
		self.img = self.IMGS[0]		# which image is used at the start

	def bounce_down(self):
		# Resets downward velocity to down (+ve)
		self.vel = START_VEL
		self.has_collided = False 	# Reset to false
		self.tick_count = 0
		self.height = self.y

	def bounce_up(self):
		self.vel = -abs(self.vel) * FRICTION 	# starting velocity?? -ve means up (SO SWAP LATER)
		self.has_collided = True		# Set to true
		self.tick_count = 0				# for keeping track of when last jumped
		self.height = self.y			# starting height (before jump)

	def move(self):
		# Called for every frame of movement
		# Sets the current velocity (vel)
		self.tick_count += 1

		d = self.vel * self.tick_count + 0.65 * self.tick_count**2 	# displacement (how many pixels are moving up or down)
		# if d >= 16:
		# 	d=16

		self.y = self.y + d 	# change current position by displacement (d)

		self.y = min(self.y,FLOOR_HEIGHT-45)

	def draw(self, win):
		self.img_count += 1		# for keeping track of how many times the img has changed

		# for automating which image to use for ball 
		if self.img_count < self.ANIMATION_TIME:
			 self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			 self.img = self.IMGS[1] 	
		elif self.img_count < self.ANIMATION_TIME*3:
			 self.img = self.IMGS[2] 	
		elif self.img_count < self.ANIMATION_TIME*4:
			 self.img = self.IMGS[1] 	
		elif self.img_count < self.ANIMATION_TIME*4+1:
			 self.img = self.IMGS[0]
			 self.img_count = 0 	

		win.blit(self.img,(self.x,self.y))

	def get_mask(self):
		return pygame.mask.from_surface(self.img)


class Pipe:
	VEL = 5				# velocity of pipe
	PIPE_HEIGHT = 640	# 550 top of pipe obstacle

	def __init__(self,x):
		self.x = x
		self.height = self.PIPE_HEIGHT
		self.top = 0
		self.imgPIPE = pipe_img 	# image of bottom pipe

		self.passed = False 		# Has the pipe been successfully navigated over

	def move(self):
		self.x -= self.VEL 	

	def draw(self,win):
		win.blit(self.imgPIPE,(self.x,self.height))

	def collide(self,oBall):
		ball_mask = oBall.get_mask()
		pipe_mask = pygame.mask.from_surface(self.imgPIPE)

		# how far away masks (ball and pipe) are from each other
		offset = (self.x - oBall.x,self.top - round(oBall.y))

		collision_flag = ball_mask.overlap(pipe_mask, offset) 	# returns null if no collision

		if collision_flag:
			return True			# Return True if collision
		return False			# Return False if collision


class Base:
	VEL = 5
	WIDTH = base_img.get_width()
	IMG = base_img

	def __init__(self,y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self,win):
		win.blit(self.IMG,(self.x1,self.y))
		win.blit(self.IMG,(self.x2,self.y))

	def collide(self,oBall):
		ball_mask = oBall.get_mask()
		base_mask = pygame.mask.from_surface(self.IMG)
		self.has_collided = True	# Set to true

		# how far away masks (ball and pipe) are from each other
		offset = (0,self.y - round(oBall.y))

		collision_flag = ball_mask.overlap(base_mask, offset) 	# returns null if no collision

		if collision_flag:
			return True			# Return True if collision
		return False			# Return False if collision


def draw_window(win,oBall,Pipes,oBase,score):
	win.blit(bg_img, (0,0))

	for oPipe in Pipes:
		oPipe.draw(win)

	oBase.draw(win)
	oBall.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1,   (255,255,255))
	win.blit(text,(WIN_WIDTH - 10 - text.get_width(),10))

	pygame.display.update()




def main():
	oBall = Ball(230,150) 	# (230,350)
	oBase = Base(FLOOR_HEIGHT)
	Pipes = [Pipe(700)] 	# 700

	clock = pygame.time.Clock()
	score = 0

	run = True
	play_live = False 	# Waits for user to press key
	while run:
		clock.tick(30) # was 30

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			# IF USER CLICKS START
			keys = pygame.key.get_pressed()	# Get list of keys pressed
			if event.type == pygame.MOUSEBUTTONDOWN or keys[pygame.K_DOWN] or keys[pygame.K_SPACE]:
				play_live = True
				oBall.bounce_down() 	# IF USER CLICKS THEN BOUNCE THE BALL DOWN

		# If ball collide with floor then reset vel for bounce up
		if oBase.collide(oBall):
			oBall.bounce_up()

		# Move the ball only after user has started
		if play_live:
			oBall.move()	

			Remove = []
			add_pipe = False
			for oPipe in Pipes:
				if oPipe.collide(oBall):
					pass
				if oPipe.x + oPipe.imgPIPE.get_width() < 0:
					Remove.append(oPipe)

				if not oPipe.passed and oPipe.x < oBall.x:
					oPipe.passed = True
					add_pipe = True

				oPipe.move()

			if add_pipe:
				score += 1
				Pipes.append(Pipe(700))

			for r in Remove:
				Pipes.remove(r)


			# OR IF FLOOR>COLLIDE???????
			if oBall.y +oBall.img.get_height() >= 730:
				pass

		oBase.move()
		draw_window(win,oBall,Pipes,oBase,score)

	pygame.quit()	# quit pygame
	quit()			# quit program

main()

