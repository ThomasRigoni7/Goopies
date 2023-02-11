import pymunk
import math
import numpy as np
from food import Food
import torch
import shapely.geometry as G
from brain import Brain

class Goopie:
    MASS = 0.05
    RADIUS = 30
    VISION_RADIUS = 150
    COLLISION_TYPE = 1
    VISION_COLLISION_TYPE = 3
    VISION_WIDTH = 16
    def __init__(self, x: float = None, y:float = None, angle:float = None, generation_range: float = 2000, generator = np.random.default_rng()) -> None:
        
        self.create_shapes(x, y, angle, generation_range, generator)
        self.sprite = None

        self.energy = 1
        self.alive = True
        self.max_turn = 0.05
        self.max_acceleration = 20
        self.max_speed = 200

        self.visual_buffer = torch.zeros((3, self.VISION_WIDTH))
        self.brain = Brain(self.VISION_WIDTH, 3)
        self.fitness: float = 0.0
    
    def create_shapes(self, x: float = None, y:float = None, angle:float = None, generation_range: float = 2000, generator = np.random.default_rng()):
        moment = pymunk.moment_for_circle(self.MASS, 0, self.RADIUS)          
        circle_body = pymunk.Body(self.MASS, moment)  
        if x is None:
            x = generator.uniform(-generation_range, generation_range)
        if y is None:
            y = generator.uniform(-generation_range, generation_range)
        circle_body.position = x, y
        circle_body.velocity = 0, 0
        circle_body.velocity_func = self.limit_velocity
        if angle is not None:
            circle_body.angle = angle
        else:
            circle_body.angle = generator.uniform(-math.pi, math.pi)
        shape = pymunk.Circle(circle_body, self.RADIUS)
        shape.elasticity = 0.4
        shape.friction = 1.0
        shape.collision_type = self.COLLISION_TYPE
        shape.goopie = self 
        self.shape = shape
        # create the vision shape
        vision_shape = pymunk.Circle(circle_body, self.VISION_RADIUS)
        vision_shape.collision_type = self.VISION_COLLISION_TYPE
        vision_shape.sensor = True
        vision_shape.goopie = self
        self.vision_shape = vision_shape

    def limit_velocity(self, body: pymunk.Body, gravity, damping, dt):
        pymunk.Body.update_velocity(body, gravity, damping, dt)
        body.angular_velocity = 0
        if body.velocity.length > self.max_speed:
            scale = self.max_speed / body.velocity.length
            body.velocity *= scale

    def get_position(self) -> pymunk.Vec2d:
        return self.shape.body.position

    def set_sprite(self, sprite):
        self.sprite = sprite

    def eat(self, food: Food) -> bool:
        """
        The goopie is colliding with food, does it eat it? What happens?
        Returns True if the goopie eats the food, False otherwise.
        """
        amount = min(1 - self.energy, food.amount)
        self.energy += amount 
        self.fitness += amount
        return True

    def is_alive(self):
        return self.alive

    def reset_vision(self):
        self.visual_buffer = torch.zeros((3, self.VISION_WIDTH))

    def update_vision(self, shape: pymunk.Shape, type: str):
        """
        Update the vision buffer with the given shape, drawing its approximate figure into the vision buffer
        """
        if type == "wall":
            # print("SEEING WALL")
            position, radius = self._calculate_approx_wall_vision(shape)
            channel = 0
        elif type == "goopie":
            # print("SEEING GOOPIE")
            other: Goopie = shape.goopie
            position = other.get_position()
            radius = other.RADIUS
            channel = 1
        elif type == "food":
            # print("SEEING FOOD")
            food: Food = shape.food
            position = food.get_position()
            radius = food.RADIUS
            channel = 2
        else:
            raise("With what are you colliding?????")
        self._update_approx_vision(position, radius, channel)

    def _update_approx_vision(self, position: pymunk.Vec2d, radius: float, channel: int):
        # the angle in radiants (-pi < angle < pi)
        vec_to_obj = position - self.get_position()
        a = position + vec_to_obj.perpendicular_normal() * radius
        b = position - vec_to_obj.perpendicular_normal() * radius
        a_angle = math.remainder(self.shape.body.angle - (a - self.get_position()).angle, math.tau)
        b_angle = math.remainder(self.shape.body.angle - (b - self.get_position()).angle, math.tau)
        a_index = math.floor((a_angle + math.pi) * (self.VISION_WIDTH / (2 * math.pi))) % self.VISION_RADIUS
        b_index = math.floor((b_angle + math.pi) * (self.VISION_WIDTH / (2 * math.pi))) % self.VISION_RADIUS
        
        distance = (position - self.get_position()).length
        activation = min(max(0, 1 - ((distance - self.RADIUS)/self.VISION_RADIUS)), 1)

        if a_index <= b_index:
            act_tensor = torch.tensor([activation]*(b_index - a_index + 1))
            self.visual_buffer[channel][a_index: b_index + 1] = torch.max(self.visual_buffer[channel][a_index: b_index + 1], act_tensor)
        else:
            act_tensor1 = torch.tensor([activation]*(b_index + 1))
            act_tensor2 = torch.tensor([activation]*(self.VISION_WIDTH - a_index))
            self.visual_buffer[channel][:b_index + 1] = torch.max(self.visual_buffer[channel][:b_index + 1], act_tensor1)
            self.visual_buffer[channel][a_index:] = torch.max(self.visual_buffer[channel][a_index:], act_tensor2)

        # print(self.visual_buffer)
        # print("a angle:", a_angle)
        # print("b angle:", b_angle)
        # print("indexes:", a_index, b_index)
        # print("vision position:", position)
        # print("vision relative position:", position - self.get_position())
        # print("vision radius:", radius)

    def _calculate_approx_wall_vision(self, wall_shape: pymunk.Segment) -> tuple[pymunk.Vec2d, float]:
        """
        Given the shape of the wall the goopie is seeing, calculates the 
        position and radius of its visible portion by the goopie.
        """
        # need to add to the radius the wall width, otherwise there could be a collision in the shapes that generates no interception
        circle = G.Point(*self.get_position()).buffer(self.VISION_RADIUS + 10).boundary
        # extend the wall such that it will always create 2 collisions, even with big vision radius of goopies in the corners
        wall_center: pymunk.Vec2d = (wall_shape.a + wall_shape.b) / 2
        a = wall_center + (wall_center - wall_shape.a) * 10
        b = wall_center + (wall_center - wall_shape.b) * 10
        line = G.LineString([a, b])
        intersection: G.MultiPoint = circle.intersection(line)
        p1 = pymunk.Vec2d(*intersection.geoms[0].coords[0])
        p2 = pymunk.Vec2d(*intersection.geoms[1].coords[0])

        position = (p1 + p2) / 2
        radius = (p1 - p2).length / 2
        return position, radius


    def step(self, dt: float):
        self.energy -= 0.1*dt
        if self.energy <= 0:
            self.alive = False

        # forward in the brain
        turn, accelerate = self.brain(self.visual_buffer, self.energy, self.shape.body.velocity.length / self.max_speed)

        # make the goopie move
        self.movement_step(turn, accelerate)

    def movement_step(self, turn: float, acceleration: float):
        """
        Updates the goopies velocity and angle based on its acceleration. Velocity will always be in the front, never laterally.
        """
        angle = self.shape.body.angle
        angle += self.max_turn * turn
        speed = self.shape.body.velocity.length
        
        velocity = speed * math.cos(angle), speed * math.sin(angle)
        self.shape.body.angle = angle
        self.shape.body.velocity = velocity
        self.shape.body.apply_force_at_local_point((acceleration * self.max_acceleration, 0), (0,0))

    def mutate(self, mutation_prob: float, mutation_amount: float):
        self.brain.mutate(mutation_prob, mutation_amount)