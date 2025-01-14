from abc import ABC, abstractmethod
import pymunk
import math
import torch
import shapely.geometry as G
from food import Food
import goopie


class Vision(ABC):

    VISION_RADIUS = 300
    VISION_COLLISION_TYPE = 3

    def __init__(self, goopie):
        self.goopie = goopie

    @abstractmethod
    def reset(self):
        ...

    @abstractmethod
    def update(self, shape: pymunk.Shape, type: str):
        ...

    def _calculate_approx_wall_vision(self, wall_shape: pymunk.Segment) -> tuple[pymunk.Vec2d, float]:
        """
        Given the shape of the wall the goopie is seeing, calculates the 
        position and radius of its visible portion by the goopie.
        """
        # need to add to the radius the wall width, otherwise there could be a collision in the shapes that generates no interception
        circle = G.Point(*self.goopie.get_position()).buffer(self.VISION_RADIUS + 10).boundary
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

class WideVision(Vision):

    VISION_BUFFER_WIDTH = 10

    def __init__(self, goopie):
        super().__init__(goopie)
        self.visual_buffer = torch.zeros((3, self.VISION_BUFFER_WIDTH))

    def reset(self):
        self.visual_buffer = torch.zeros((3, self.VISION_BUFFER_WIDTH))

    def update(self, shape: pymunk.Shape, type: str):
        """
        Update the vision buffer with the given shape, drawing its approximate figure into the vision buffer
        """
        if type == "wall":
            # print("SEEING WALL")
            position, radius = self._calculate_approx_wall_vision(shape)
            channel = 0
        elif type == "goopie":
            # print("SEEING GOOPIE")
            other : goopie.Goopie = shape.goopie
            position = other.get_position()
            radius = other.RADIUS
            channel = 1
        elif type == "food":
            # print("SEEING FOOD")
            food : Food = shape.food
            position = food.get_position()
            radius = food.RADIUS
            channel = 2
        else:
            raise("With what are you colliding?????")
        self._update_approx_vision(position, radius, channel)

    def _update_approx_vision(self, position: pymunk.Vec2d, radius: float, channel: int):
        # the angle in radiants (-pi < angle < pi)
        vec_to_obj = position - self.goopie.get_position()
        a = position + vec_to_obj.perpendicular_normal() * radius
        b = position - vec_to_obj.perpendicular_normal() * radius
        a_angle = math.remainder(self.goopie.shape.body.angle - (a - self.goopie.get_position()).angle, math.tau)
        b_angle = math.remainder(self.goopie.shape.body.angle - (b - self.goopie.get_position()).angle, math.tau)
        a_index = math.floor((a_angle + math.pi) * (self.VISION_BUFFER_WIDTH / (2 * math.pi))) % self.VISION_RADIUS
        b_index = math.floor((b_angle + math.pi) * (self.VISION_BUFFER_WIDTH / (2 * math.pi))) % self.VISION_RADIUS
        
        distance = (position - self.goopie.get_position()).length
        activation = min(max(0, 1 - ((distance - self.goopie.RADIUS)/self.VISION_RADIUS)), 1)

        if a_index <= b_index:
            act_tensor = torch.tensor([activation]*(b_index - a_index + 1))
            self.visual_buffer[channel][a_index: b_index + 1] = torch.max(self.visual_buffer[channel][a_index: b_index + 1], act_tensor)
        else:
            act_tensor1 = torch.tensor([activation]*(b_index + 1))
            act_tensor2 = torch.tensor([activation]*(self.VISION_BUFFER_WIDTH - a_index))
            self.visual_buffer[channel][:b_index + 1] = torch.max(self.visual_buffer[channel][:b_index + 1], act_tensor1)
            self.visual_buffer[channel][a_index:] = torch.max(self.visual_buffer[channel][a_index:], act_tensor2)

        # print(self.visual_buffer)
        # print("a angle:", a_angle)
        # print("b angle:", b_angle)
        # print("indexes:", a_index, b_index)
        # print("vision position:", position)
        # print("vision relative position:", position - self.get_position())
        # print("vision radius:", radius)

class ClosestVision(Vision):
    """
    distances are between the surface of the shapes, angles are 0-2*pi
    """

    def __init__(self, goopie):
        super().__init__(goopie)
        self.closest_food_distance = self.VISION_RADIUS
        self.closest_goopie_distance = self.VISION_RADIUS
        self.closest_wall_distance = self.VISION_RADIUS
        self.closest_food_angle = 0
        self.closest_goopie_angle = 0
        self.closest_wall_angle = 0

    def update(self, shape: pymunk.Shape, type: str):
        my_pos = self.goopie.get_position()
        my_radius = self.goopie.RADIUS
        other_pos: pymunk.Vec2d = shape.body.position

        if type == "wall":
            position, _ = self._calculate_approx_wall_vision(shape)
            distance = (my_pos - position).length
            if distance < self.closest_wall_distance:
                self.closest_wall_distance = distance
                self.closest_wall_angle = math.remainder(self.goopie.shape.body.angle - (my_pos - other_pos).angle, math.tau)

            if distance < self.closest_wall_distance:
                self.closest_wall_distance = distance
                self.closest_wall_angle = angle
        else:
            other_radius = shape.body.radius
            distance = (my_pos - other_pos).length - (my_radius + other_radius)
            angle = math.remainder(self.goopie.shape.body.angle - (my_pos - other_pos).angle, math.tau)

            if type == "goopie":
                if distance < self.closest_goopie_distance:
                    self.closest_goopie_distance = distance
                    self.closest_goopie_angle = angle
            if type == "food":
                if distance < self.closest_food_distance:
                    self.closest_food_distance = distance
                    self.closest_food_angle = angle
            

    def reset(self):
        self.closest_food_distance = self.VISION_RADIUS
        self.closest_goopie_distance = self.VISION_RADIUS
        self.closest_wall_distance = self.VISION_RADIUS
        self.closest_food_angle = 0
        self.closest_goopie_angle = 0
        self.closest_wall_angle = 0