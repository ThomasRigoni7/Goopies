import pymunk
from goopie import Goopie
from food import Food
import numpy as np
import math

class Simulation:
    WALL_COLLISION_TYPE = 4
    def __init__(self, num_goopies, num_food, space_size, test: bool = False) -> None:
        super().__init__()
        # create all the goopies, food and walls together with pymunk objects for everything
        self.space_size = space_size
        self.test = test
        self.generator = np.random.default_rng()
        self.space: pymunk.Space = pymunk.Space()
        self.window = None
        self.set_collision_handlers()
        
        self.create_walls()

        self.goopies :list[Goopie] = []
        for _ in range(num_goopies):
            if test:
                goopie1 = Goopie(0, 0, math.pi/4)
                goopie2 = Goopie(50, 50, math.pi/4)
                self.add_goopie(goopie1)
                self.add_goopie(goopie2)
            else:
                goopie = Goopie(generation_range=self.space_size * 0.8)
                self.add_goopie(goopie)
        
        self.foods :list[Food] = []
        for _ in range(num_food):
            if test:
                # food1 = Food(50, 50)
                # food2 = Food(-50, 50)
                # self.add_food(food1)
                # self.add_food(food2)
                pass
            else:
                food = Food(generation_range=space_size * 0.9)
                self.add_food(food)

    def set_collision_handlers(self):
        goopie_food_collision_handler = self.space.add_collision_handler(Goopie.COLLISION_TYPE, Food.COLLISION_TYPE)
        vision_food_collision_handler = self.space.add_collision_handler(Goopie.VISION_COLLISION_TYPE, Food.COLLISION_TYPE)
        vision_goopie_collision_handler = self.space.add_collision_handler(Goopie.VISION_COLLISION_TYPE, Goopie.COLLISION_TYPE)
        vision_wall_collision_handler = self.space.add_collision_handler(Goopie.VISION_COLLISION_TYPE, self.WALL_COLLISION_TYPE)

        goopie_food_collision_handler.pre_solve = self.goopie_food_collision
        vision_food_collision_handler.pre_solve = self.vision_food_collision
        vision_goopie_collision_handler.pre_solve = self.vision_goopie_collision
        vision_wall_collision_handler.pre_solve = self.vision_wall_collision


    def goopie_food_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        goopie:Goopie = arbiter.shapes[0].goopie
        food:Food = arbiter.shapes[1].food
        if food in self.foods:
            if goopie.eat(food):
                self.remove_food(food)
        return False

    def vision_food_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        goopie:Goopie = arbiter.shapes[0].goopie
        goopie.update_vision(arbiter.shapes[1], "food")
        return False
    
    def vision_goopie_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        goopie:Goopie = arbiter.shapes[0].goopie
        goopie.update_vision(arbiter.shapes[1], "goopie")
        return False

    def vision_wall_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        goopie:Goopie = arbiter.shapes[0].goopie
        goopie.update_vision(arbiter.shapes[1], "wall")
        return False
    
    def create_walls(self):
        self.walls = [
            pymunk.Segment(self.space.static_body, (self.space_size, self.space_size), (self.space_size, -self.space_size), 10),
            pymunk.Segment(self.space.static_body, (self.space_size, -self.space_size), (-self.space_size, -self.space_size), 10),
            pymunk.Segment(self.space.static_body, (-self.space_size, -self.space_size), (-self.space_size, self.space_size), 10),
            pymunk.Segment(self.space.static_body, (-self.space_size, self.space_size), (self.space_size, self.space_size), 10)
        ]
        # if self.test:
        #     self.walls.append(pymunk.Segment(self.space.static_body, (130, 90), (200, 0), 10))

        for wall in self.walls:
            wall.collision_type = self.WALL_COLLISION_TYPE
            wall.elasticity = 0.8
            wall.friction = 1.0
            self.space.add(wall)

    def remove_goopie(self, goopie: Goopie):
        self.goopies.remove(goopie)
        self.space.remove(goopie.shape.body)
        self.space.remove(goopie.shape)
        if goopie.sprite is not None:
            goopie.sprite.kill()

    def remove_food(self, food: Food):
        self.foods.remove(food)
        self.space.remove(food.shape.body)
        self.space.remove(food.shape)
        if food.sprite is not None:
            food.sprite.kill()

    def add_goopie(self, goopie: Goopie):
        self.space.add(goopie.shape.body, goopie.shape, goopie.vision_shape)
        self.goopies.append(goopie)
    
    def add_food(self, food: Food):
        self.space.add(food.shape.body, food.shape)
        self.foods.append(food)

    def step(self):
        dt = 0.01

        for goopie in self.goopies:
            goopie.reset_vision()

        self.space.step(dt)
        for goopie in self.goopies:
            goopie.step(dt)
            if not goopie.is_alive():
                self.remove_goopie(goopie)
        
    def run(self, headless: bool = False):
        from window import GameWindow
        update_rate = 1e-5 if headless else 1/60
        self.window = GameWindow(self, update_rate)
        self.window.run()