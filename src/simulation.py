import pymunk
from goopie import Goopie
from food import Food
import numpy as np
import torch
import math
import timeit

class Simulation:
    WALL_COLLISION_TYPE = 4
    def __init__(self, num_goopies, num_food, space_size, test: bool = False, respawn_rate: float = 0.5, mutation_prob = 0.5, mutation_amount = 0.1) -> None:
        super().__init__()
        self.num_goopies = num_goopies
        self.num_food = num_food
        self.space_size = space_size
        self.test = test
        self.respawn_rate = respawn_rate
        self.mutation_prob = mutation_prob
        self.mutation_amount = mutation_amount

        self.goopie_spawn_range = space_size * 0.8
        self.food_spawn_range = space_size * 0.9

        # create all the goopies, food and walls together with pymunk objects for everything
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
                goopie = Goopie(generation_range=self.goopie_spawn_range, generator=self.generator)
                self.add_goopie(goopie)
        
        self.foods :list[Food] = []
        for _ in range(num_food):
            if test:
                food1 = Food(25, 25)
                # food2 = Food(-50, 50)
                self.add_food(food1)
                # self.add_food(food2)
                pass
            else:
                food = Food(generation_range=self.food_spawn_range, generator=self.generator)
                self.add_food(food)
        
        self.best_goopies: list[Goopie] = []
        self.fitness_thresh = 0
        self.best_fitness = 0


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
                new_food = Food(generation_range=self.food_spawn_range, generator=self.generator)
                self.add_food(new_food)
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
        self.space.remove(goopie.vision_shape)
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
        if self.window is not None and not self.window.headless:
            self.window.add_goopie_sprite(goopie)
    
    def add_food(self, food: Food):
        self.space.add(food.shape.body, food.shape)
        self.foods.append(food)
        if self.window is not None and not self.window.headless:
            self.window.add_food_sprite(food)

    def step(self):
        dt = 0.01

        for goopie in self.goopies:
            goopie.reset_vision()

        space_step_start_time = timeit.default_timer()
        self.space.step(dt)
        self.space_time = timeit.default_timer() - space_step_start_time

        goopie_step_start_time = timeit.default_timer()
        for goopie in self.goopies:
            goopie.step(dt)
            if not goopie.is_alive():
                self.remove_goopie(goopie)
                self.update_best_goopies(goopie)
                if len(self.goopies) < self.num_goopies:
                    self.spawn_goopie(self.respawn_rate, self.mutation_prob, self.mutation_amount)

        self.goopie_time = timeit.default_timer() - goopie_step_start_time
        
    def update_best_goopies(self, goopie: Goopie):
        if goopie.fitness > self.fitness_thresh:
            self.best_goopies.append(goopie)
            self.best_goopies.sort(key= lambda g: g.fitness, reverse=True)
            if len(self.best_goopies) > 10:
                self.best_goopies.pop(10)
            self.fitness_thresh = self.best_goopies[-1].fitness
            self.best_fitness = self.best_goopies[0].fitness
    
    def spawn_goopie(self, random_prob: float, mutation_prob: float, mutation_amount: float):
        random_spawn = self.generator.uniform() < random_prob
        goopie = Goopie(generation_range=self.goopie_spawn_range, generator=self.generator)
        if len(self.best_goopies) > 0 and not random_spawn:
            # load nn from one of the best fit goopies
            probs = torch.nn.functional.softmax(torch.tensor([g.fitness / 3 for g in self.best_goopies]), dim=0)
            index = int(torch.distributions.Categorical(probs=probs).sample())
            goopie.brain.load_state_dict(self.best_goopies[index].brain.state_dict())
            goopie.mutate(mutation_prob, mutation_amount)
        self.add_goopie(goopie)
        return goopie


    def run(self, headless: bool = False):
        from window import GameWindow
        update_rate = 1e-5 if headless else 1/60
        self.window = GameWindow(self, update_rate)
        self.window.run()