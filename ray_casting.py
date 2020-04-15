#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import random

import pyglet
from pyglet.window import key
from pyglet.window import mouse

HEIGHT = 900
WIDTH = 1200


def dot(p1, p2):
    return (p1[0] * p2[0] + p1[1] * p2[1])


def draw_line(x1, y1, x2, y2):
    pyglet.gl.glVertex2f(x1, y1)
    pyglet.gl.glVertex2f(x2, y2)


class Wall():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self):
        draw_line(self.x1, self.y1, self.x2, self.y2)


class Emitter():

    def __init__(self, x, y, v1=0, v2=0, num_directions=10, tol=1e-8):
        self.x = x
        self.y = y
        self.v1 = v1
        self.v2 = v2
        self.num_directions = num_directions
        self.tol = tol
        self.initialize_directions(x, y, num_directions)

    def initialize_directions(self, x, y, num_directions):
        angles = [i * 2 * math.pi / num_directions for i in range(num_directions)]
        self.directions = [(math.cos(angle), math.sin(angle)) for angle in angles]

    def set_directions(self, *args):
        self.directions = [(arg[0] - self.x, arg[1] - self.y) for arg in args]

    def set_center(self, x, y):
        self.x = x
        self.y = y

    def set_velocity(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def check_collision(self, walls):
        lambda_min = math.inf
        collision = False
        min_wall = None
        new_point = None
        new_velocity = None
        for wall in walls:
            denom = self.v1 * (wall.y1 - wall.y2) - self.v2 * (wall.x1 - wall.x2)
            if abs(denom) < self.tol:
                continue
            lambda_ = ((wall.y1 - wall.y2) * (wall.x1 - self.x) + (wall.x2 - wall.x1) * (wall.y1 - self.y)) / denom
            mu = (self.v1 * (wall.y1 - self.y) - self.v2 * (wall.x1 - self.x)) / denom
            if (0 <= mu) and (mu <= 1) and (0 <= lambda_) and (lambda_ <= 1):
                if lambda_ < lambda_min:
                    lambda_min = lambda_
                    min_wall = wall
                    collision = True
        if collision:
            new_point = (self.x + lambda_min * self.v1, self.y + lambda_min * self.v2)
            n = (min_wall.y1 - min_wall.y2, min_wall.x2 - min_wall.x1)
            beta = -2 * dot(n, (self.v1, self.v2)) / dot(n, n)
            new_velocity = (1.001*(self.v1 + beta * n[0]), 1.001*(self.v2 + beta * n[1]))
            #print(f"MAGNITUDE: {dot(new_velocity, new_velocity)}")
            new_point = (new_point[0] + (1 - lambda_min) * new_velocity[0], new_point[1] + (1 - lambda_min) * new_velocity[1])
        return new_point, new_velocity

    def update_position(self, walls):
        new_point, new_velocity = self.check_collision(walls)
        if not new_point:
            self.set_center(self.x + self.v1, self.y + self.v2)
        else:
            self.set_center(*new_point)
            self.set_velocity(*new_velocity)

    def detect_ray_endpoint(self, direction, walls):
        t_min = math.inf
        point = None
        for wall in walls:
            denom = direction[0] * (wall.y2 - wall.y1) - direction[1] * (wall.x2 - wall.x1)
            if abs(denom) < self.tol:
                continue
            t = ((wall.y2 - wall.y1) * (wall.x2 - self.x) + (wall.x1 - wall.x2) * (wall.y2 - self.y)) / denom
            lambda_ = (direction[0] * (wall.y2 - self.y) - direction[1] * (wall.x2 - self.x)) / denom
            if (t < 0) or (lambda_ > 1) or (lambda_ < 0):
                continue
            if t < t_min:
                t_min = t
                point = (self.x + t * direction[0], self.y + t * direction[1])
        return point

    def connect(self, point):
        draw_line(self.x, self.y, point[0], point[1])

    def draw_rays(self, walls):
        for direction in self.directions:
            point = self.detect_ray_endpoint(direction, walls)
            if point:
                self.connect(point)


def draw_rectangle(x=1, y=1, height=HEIGHT, width=WIDTH):
    walls = []
    # left border
    walls.append(Wall(x, y, x, y + height - 1))
    # right border
    walls.append(Wall(x + width-1, y, x + width - 1, y + height - 1))
    # bottom border
    walls.append(Wall(x, y, x + width - 1, y))
    # top border
    walls.append(Wall(x, y + height - 1, x + width - 1, y + height - 1))
    return walls


def generate_random_wall():
    return Wall(random.randint(1, WIDTH), random.randint(1, HEIGHT), random.randint(1, WIDTH), random.randint(1, HEIGHT))


x = 600  # random.randint(100, WIDTH - 100)
y = 450  # random.randint(100, HEIGHT - 100)
v1 = 10
v2 = 10
emitter = Emitter(x, y, v1, v2, 200)
walls = draw_rectangle()

for i in range(5):
    walls.append(generate_random_wall())


def update_center(dt):
    global emitter
    global walls
    #if emitter.check_collision(walls):
    #    emitter.set_velocity(-emitter.v1, -emitter.v2 + 0.01)
    emitter.update_position(walls)


window = pyglet.window.Window(height=HEIGHT, width=WIDTH)
pyglet.clock.schedule_interval(update_center, 1/60)


@window.event
def on_draw():
    global emitter
    window.clear()
    pyglet.gl.glBegin(pyglet.gl.GL_LINES)
    for wall in walls:
        wall.draw()
    emitter.draw_rays(walls)
    pyglet.gl.glEnd()
    return None


@window.event
def on_mouse_press(x, y, button, modifiers):
    global emitter
    if button == mouse.LEFT:
        emitter.set_center(x, y)
        print(f'The left mouse button was pressed at {(x, y)}')

pyglet.app.run()
