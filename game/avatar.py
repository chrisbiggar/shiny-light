'''

'''

import math
import pyglet
from pyglet import *
from pyglet.window import key
import pymunk
from pymunk.vec2d import Vec2d
import py2d
from py2d.director import Director
from py2d import actor
from py2d import keyboard

dx = 150

platform_collType = 1

PLAYER_VELOCITY = 200.
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = (PLAYER_VELOCITY / PLAYER_GROUND_ACCEL_TIME)

PLAYER_AIR_ACCEL_TIME = 0.05
PLAYER_AIR_ACCEL = (PLAYER_VELOCITY/PLAYER_AIR_ACCEL_TIME)

JUMP_HEIGHT = 48
JUMP_BOOST_HEIGHT = 24.
JUMP_CUTOFF_VELOCITY = 100
FALL_VELOCITY = 500.
JUMP_LENIENCY = 0.05
HEAD_FRICTION = 0.7

JUMP_TIMES = 2


class Avatar(py2d.actor.PhysicalActor):
	keyboard = keyboard.Keyboard()
	remaining_jumps = 0
	

	def __init__(self, window, batch=None):
		anim = self.loadAnimation("zombieright.png", 1, 4, 0.1, True, True)
		super(Avatar, self).__init__(anim, batch)
		window.push_handlers(self.keyboard)
		self.keyboard.keyPressHandler = self.keyRelease
		self.initPhysics()
		#self.landing = {'p':Vec2d.zero(), 'n':0}
		self.landed_previous = False
		self.jumpTrigger = False
		
	def initPhysics(self):
		self.feet = pymunk.Circle(self.body, 20, (0,0))
		self.mid = pymunk.Circle(self.body, 20, (0,40))
		self.head = pymunk.Circle(self.body, 20, (0,75))
		self.feet.collisionType = platform_collType
		self.feet.elasticity = 1.
		
		self.platformNormal = Vec2d.zero()
		self.platformBody = None
		
		self.slide = False

	def addedToScene(self, scene):
		super(Avatar, self).addedToScene(scene)
		scene.space.add(self.feet)
		scene.space.add(self.mid)
		scene.space.add(self.head)

	def keyRelease(self, symbol, modifier):
		if symbol == key.M:
			self.body.angle += math.radians(40)
		
		if symbol == key.UP:
			self.jumpTrigger = True

	def set_position(self,x,y):
		self.body.position = x,y
		super(Avatar, self).set_position(x,y)


	def update(self, dt):
		def f(arbiter):
			n = -arbiter.contacts[0].normal
			if n.y > 0.0:
				self.platformNormal = n
				self.platformBody = arbiter.shapes[1].body
		
		self.platformNormal = Vec2d.zero()
		self.platformBody = None
		self.body.each_arbiter(f)
		
		# if ground body is found and slope induced grounding normal is lower than feet friction
		# (find out if grounded)
		grounded = False
		ground_velocity = Vec2d.zero()
		if self.platformBody != None and abs(self.platformNormal.x / self.platformNormal.y) < self.feet.friction:
			grounded = True
			self.remaining_jumps = JUMP_TIMES
			ground_velocity = self.platformBody.velocity
			
		# control inputs
		targetXVel = 0
		if self.keyboard[key.LEFT]:
			targetXVel -= PLAYER_VELOCITY
		if self.keyboard[key.RIGHT]:
			targetXVel += PLAYER_VELOCITY
		if self.keyboard[key.DOWN]:
			self.slide = True
		else:
			self.slide = False
		if self.jumpTrigger == True:
			self.jumpTrigger = False
			if grounded or self.remaining_jumps > 0:
				#add target jump velocity to body
				jumpVel = math.sqrt(2.0 * JUMP_HEIGHT * abs(self.scene.space.gravity.y))
				self.body.velocity.y = ground_velocity.y + jumpVel
				self.remaining_jumps -=1
		
		# if on ground
		if self.platformBody != None:
			# if slide key and on slope (normal is (0,1) when on level ground)
			if self.slide == True and (self.platformNormal.x / self.platformNormal.y) != 0.:
				self.feet.friction = 0
			else:
				self.feet.friction = abs(PLAYER_GROUND_ACCEL / self.scene.space.gravity.y)
			self.head.friciton = HEAD_FRICTION
			# apply target x velocity to surface velocity of feet..
			self.feet.surface_velocity = targetXVel, 0
		else:
			self.feet.friction,self.head.friction = 0,0
			self.body.apply_impulse((targetXVel/6,0))
			
		# fall rate limiter
		self.body.velocity.y = max(self.body.velocity.y, -FALL_VELOCITY) # clamp upwards as well?
			
		super(Avatar, self).update(dt)
		
		
		
		
		
