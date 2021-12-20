from __future__ import division
from __future__ import absolute_import

######################################################################
# This file copyright the Georgia Institute of Technology
#
# Permission is given to students to use or modify this file (only)
# to work on their assignments.
#
# You may NOT publish this file or make it available to others not in
# the course.
#
######################################################################

import time
import turtle

import runner


# Set DEBUG_DISPLAY to True to see the meteorite ID numbers and the labels of
# the corners of the arena in the GUI.
# DEBUG_DISPLAY = True
DEBUG_DISPLAY = True


class TurtleRunnerDisplay(runner.BaseRunnerDisplay):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x_bounds = (0.0, 1.0)
        self.y_bounds = (0.0, 1.0)
        self.meteorite_turtles = {}
        self.estimated_meteorite_turtles = {}
        self.turret_turtle = turtle.Turtle()
        self.turret_turtle.radians()
        self.laser_turtle = turtle.Turtle()
        self.laser_turtle.radians()
        self.laser_len = 2.0
        self.turret_loc = {}
        self.time_turtle = turtle.Turtle()

    def setup(self, x_bounds, y_bounds,
              in_bounds,
              margin,
              noise_sigma,
              turret,
              max_angle_change):
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.margin = margin
        xmin, xmax = x_bounds
        ymin, ymax = y_bounds
        dx = xmax - xmin
        dy = ymax - ymin
        turtle.setup(width=self.width, height=self.height)
        turtle.setworldcoordinates(xmin - (dx * margin),
                                   ymin - (dy * margin),
                                   xmax + (dx * margin),
                                   ymax + (dy * margin))
        turtle.tracer(0, 1)

        self._draw_inbounds(in_bounds)

        self.turret_turtle.shape("classic")
        self.turret_turtle.color("black")
        self.turret_turtle.shapesize(self.margin * 10, self.margin * 10)
        self.turret_turtle.penup()
        self.turret_loc['x_coord'] = turret.x_pos
        self.turret_loc['y_coord'] = turret.y_pos
        self.turret_turtle.setposition(self.turret_loc['x_coord'],
                                       self.turret_loc['y_coord'])
        self.time_turtle.setposition(self.turret_loc['x_coord'] + 0.3,
                                     self.turret_loc['y_coord'])

    def _draw_inbounds(self, in_bounds):
        t = turtle.Turtle()
        t.hideturtle()
        t.shapesize(0.00001, 0.00001)
        t.pencolor("black")
        t.penup()
        t.setposition(in_bounds.x_bounds[0], in_bounds.y_bounds[0])
        t.pendown()
        t.setposition(in_bounds.x_bounds[1], in_bounds.y_bounds[0])
        if DEBUG_DISPLAY: t._write('({}, {})'.format(in_bounds.x_bounds[1], in_bounds.y_bounds[0]), 'center', 'arial')
        t.setposition(in_bounds.x_bounds[1], in_bounds.y_bounds[1])
        if DEBUG_DISPLAY: t._write('({}, {})'.format(in_bounds.x_bounds[1], in_bounds.y_bounds[1]), 'center', 'arial')
        t.setposition(in_bounds.x_bounds[0], in_bounds.y_bounds[1])
        if DEBUG_DISPLAY: t._write('({}, {})'.format(in_bounds.x_bounds[0], in_bounds.y_bounds[1]), 'center', 'arial')
        t.setposition(in_bounds.x_bounds[0], in_bounds.y_bounds[0])
        if DEBUG_DISPLAY: t._write('({}, {})'.format(in_bounds.x_bounds[0], in_bounds.y_bounds[0]), 'center', 'arial')
        t.showturtle()

    def begin_time_step(self, t):
        """Set up turtles for the beginning of current timestep t."""
        self.time_turtle.clear()
        self.time_turtle.hideturtle()
        self.time_turtle.shape("circle")
        self.time_turtle.shapesize(0.0001 * self.margin, 0.0001 * self.margin)
        self.time_turtle._write("\nTime: {0}".format(t), 'center', 'arial')
        self.time_turtle.showturtle()
        for idx, trtl in list(self.meteorite_turtles.items()):
            trtl.clear()
            trtl.hideturtle()
        for idx, trtl in list(self.estimated_meteorite_turtles.items()):
            trtl.clear()
            trtl.hideturtle()
        self.turret_turtle.clear()
        self.turret_turtle.hideturtle()
        self.laser_turtle.clear()
        self.laser_turtle.hideturtle()
        self._laser_go_home()
        # turtle.update()

    def meteorite_at_loc(self, i, x, y):
        if i < 0:
            # meteorite is deactivated; don't show
            return
        if i not in self.meteorite_turtles:
            trtl = turtle.Turtle()
            trtl.shape("circle")
            trtl.color("grey")
            trtl.shapesize(self.margin * 15, self.margin * 15)
            trtl.penup()
            self.meteorite_turtles[i] = trtl
        self.meteorite_turtles[i].setposition(x, y)
        # Uncomment the following line to display meteorite IDs
        if DEBUG_DISPLAY: self.meteorite_turtles[i]._write(str(i), 'center', 'arial')
        self.meteorite_turtles[i].showturtle()

    def meteorite_estimated_at_loc(self, i, x, y, is_match=False):
        if i < 0:
            # meteorite is deactivated; don't show
            return
        if i not in self.estimated_meteorite_turtles:
            trtl = turtle.Turtle()
            trtl.shape("circle")
            trtl.color("#88ff88" if is_match else "#aa4444")
            trtl.shapesize(0.2, 0.2)
            trtl.penup()
            self.estimated_meteorite_turtles[i] = trtl
        self.estimated_meteorite_turtles[i].color("#88ff88" if is_match else "#aa4444")
        self.estimated_meteorite_turtles[i].setposition(x, y)
        self.estimated_meteorite_turtles[i].showturtle()

    def turret_at_loc(self, hdg):
        # self.turret_turtle.setposition(x, y)
        if hdg is not None:
            self.turret_turtle.setheading(hdg)
            self.turret_turtle.shapesize(2, 2)
        self.turret_turtle.showturtle()

    def turret_health(self, hp, hp0):
        self.turret_turtle._write("\n{0}/{1} HP".format(int(hp), int(hp0)), 'center', 'arial')

    def laser_target_heading(self, rad, laser_len=2.0):
        self._laser_go_home()
        self.laser_turtle.color("red")
        self.laser_turtle.setheading(rad)
        self.laser_turtle.pendown()
        self.laser_turtle.forward(laser_len)
        self.laser_turtle.penup()
        self.laser_turtle.showturtle()

    def end_time_step(self, t):
        turtle.update()
        time.sleep(0.1)

    def teardown(self):
        turtle.done()

    def laser_destruct(self):
        self._explode_turret()

    def _explode_turret(self):
        self.turret_turtle.shape("circle")
        self.turret_turtle.shapesize(10, 10)
        self.turret_turtle.color("orange")

    def _laser_go_home(self):
        """Send laser's turtle back to its home location, but keep heading."""
        self.laser_turtle.setposition(self.turret_loc['x_coord'],
                                      self.turret_loc['y_coord'])
