# -*- coding: utf-8 -*-
# In this exercise, write a program that will
# run your previous code twice.
# Please only modify the indicated area below!

from math import *
import random

landmarks = [[20.0, 20.0], [80.0, 80.0], [20.0, 80.0], [80.0, 20.0]]
world_size = 100.0


class robot(object):
    def __init__(self, length = 20):
        self.x = random.random() * world_size
        self.y = random.random() * world_size
        self.orientation = random.random() * 2.0 * pi
        self.forward_noise = 0.0;
        self.turn_noise = 0.0;
        self.sense_noise = 0.0;
        self.length = length

    def set(self, new_x, new_y, new_orientation):
        if new_x < 0 or new_x >= world_size:
            raise ValueError('X coordinate out of bound')
        if new_y < 0 or new_y >= world_size:
            raise ValueError('Y coordinate out of bound')
        if new_orientation < 0 or new_orientation >= 2 * pi:
            raise ValueError('Orientation must be in [0..2pi]')
        self.x = float(new_x)
        self.y = float(new_y)
        self.orientation = float(new_orientation)

    def set_noise(self, new_f_noise, new_t_noise, new_s_noise):
        # makes it possible to change the noise parameters
        # this is often useful in particle filters
        self.forward_noise = float(new_f_noise);
        self.turn_noise = float(new_t_noise);
        self.sense_noise = float(new_s_noise);

    def sense(self):
        Z = []
        for i in range(len(landmarks)):
            dist = sqrt((self.x - landmarks[i][0]) ** 2 + (self.y - landmarks[i][1]) ** 2)
            dist += random.gauss(0.0, self.sense_noise)
            Z.append(dist)
        return Z

    def move(self, turn, forward):
        if forward < 0:
            raise ValueError('Robot cant move backwards')

        # turn, and add randomness to the turning command
        orientation = self.orientation + float(turn) + random.gauss(0.0, self.turn_noise)
        orientation %= 2 * pi

        # move, and add randomness to the motion command
        dist = float(forward) + random.gauss(0.0, self.forward_noise)
        x = self.x + (cos(orientation) * dist)
        y = self.y + (sin(orientation) * dist)
        x %= world_size  # cyclic truncate
        y %= world_size

        # set particle
        res = robot()
        res.set(x, y, orientation)
        res.set_noise(self.forward_noise, self.turn_noise, self.sense_noise)
        return res

    def Gaussian(self, mu, sigma, x):

        # calculates the probability of x for 1-dim Gaussian with mean mu and var. sigma
        return exp(- ((mu - x) ** 2) / (sigma ** 2) / 2.0) / sqrt(2.0 * pi * (sigma ** 2))

    def measurement_prob(self, measurement):

        # calculates how likely a measurement should be

        prob = 1.0;
        for i in range(len(landmarks)):
            dist = sqrt((self.x - landmarks[i][0]) ** 2 + (self.y - landmarks[i][1]) ** 2)
            prob *= self.Gaussian(dist, self.sense_noise, measurement[i])
        return prob

    def __repr__(self):
        return '[x=%.6s y=%.6s orient=%.6s]' % (str(self.x), str(self.y), str(self.orientation))

    def q4_move(self, motion):
        # You can replace the INSIDE of this function with the move function you modified in the Udacity quiz
        # Make sure your implementation handles cases when the robot has non-zero noise.
        alpha = motion[0]
        theta = self.orientation
        distance = motion[1]
        beta = distance * tan(alpha) / self.length
        if (beta > 0.001):
            R = distance / beta
            cx = self.x - sin(theta) * R
            cy = self.y + cos(theta) * R
            xp = cx + sin(theta+beta) * R
            yp = cy - cos(theta+beta) * R
            thetan = (theta + beta)
            thetan %= 2 * pi
        else:
            xp = self.x + distance * cos(theta)
            yp = self.y + distance * sin(theta)
            thetan = theta

        res = self
        res.set(xp, yp, thetan)
        #res.set_noise(self.forward_noise,self.turn_noise,self.sense_noise)
        #print(motion)

        return res  # make sure your move function returns an instance
        # of the robot class with the correct coordinates.

    def q5_sense(self, add_noise):
        # You can replace the INSIDE of this function with the sense function you modified in the Udacity quiz
        # You can ignore add_noise for Q5
        Z = []
        # ENTER CODE HERE
        # HINT: You will probably need to use the function atan2()
        for i in range(len(landmarks)):
            dx = self.x - landmarks[i][0]
            dy = self.y - landmarks[i][1]
            Z.append(atan2(-dy,-dx) - self.orientation)

        return Z  # Leave this line here. Return vector Z of 4 bearings.

length = 20
myrobot = robot(length)
steering_noize = 0.0
distance_noise = 0.0
myrobot.set_noise(0.,0.,0.)
myrobot.set(30.,20.,0.)
myrobot.q5_sense(0.0)
print(myrobot)
print(myrobot.q5_sense(0.0))

'''
motions = [[0.0,10.0],[pi/6.0,10.0],[0.0,20.0]]
for i in range(len(motions)):
    myrobot = myrobot.q4_move(motions[i])
    print (myrobot)
    '''



