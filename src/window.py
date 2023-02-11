import arcade
import timeit
from math import degrees, pi
import pyglet

from simulation import Simulation
from goopie import Goopie
from food import Food

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
WINDOW_TITLE = "GOOPIES SIMULATION"

GOOPIE_IMAGE_SIZE = 460
FOOD_IMAGE_SIZE = 460

class GameWindow(arcade.Window):
    def __init__(self, simulation: Simulation, update_rate: float = 1/60):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, update_rate=update_rate)
        self.set_location(400, 200)
        self.background_color = arcade.color.DARK_SLATE_GRAY
        self.simulation = simulation

        self.camera = arcade.Camera()
        P = pyglet.math.Mat4.orthogonal_projection(-simulation.space_size, simulation.space_size, -simulation.space_size, simulation.space_size, -255, 255)
        # P = pyglet.math.Mat4.orthogonal_projection(-100, 100, -100, 100, -255, 255)
        # print(P)
        self.camera.projection_matrix = P

        self.goopie_sprites = arcade.SpriteList()
        for goopie in simulation.goopies:
            self.add_goopie_sprite(goopie)

        self.food_sprites = arcade.SpriteList(use_spatial_hash=True)
        for food in simulation.foods:
            self.add_food_sprite(food)
        
        self.draw_time = 0
        self.frame = 0

    def add_goopie_sprite(self, goopie: Goopie):
        scale = 2 * goopie.RADIUS / GOOPIE_IMAGE_SIZE
        sprite = arcade.Sprite("./sprites/goopie.png", scale)
        x, y = goopie.get_position()
        sprite.set_position(x, y)
        goopie.set_sprite(sprite)
        self.goopie_sprites.append(sprite)

    def add_food_sprite(self, food: Food):
        scale = 2 * food.RADIUS / GOOPIE_IMAGE_SIZE
        sprite = arcade.Sprite("./sprites/food.png", scale)
        x, y = food.get_position()
        sprite.set_position(x, y)
        food.set_sprite(sprite)
        self.food_sprites.append(sprite)

    def on_draw(self):
        if self.headless:
            return
        
        self.clear()
        self.camera.use()

        draw_start_time = timeit.default_timer()
        arcade.start_render()

        self.goopie_sprites.draw()
        self.food_sprites.draw()

        for goopie in self.simulation.goopies:
            arcade.draw_circle_outline(*goopie.get_position(), Goopie.VISION_RADIUS, arcade.color.YELLOW)
        
        # draw walls
        for wall in self.simulation.walls:
            arcade.draw_lines([wall.a, wall.b], arcade.color.RED, 20)

        last_fitness = 0
        if len(self.simulation.best_goopies) > 0:
            last_fitness = self.simulation.best_goopies[-1].fitness
        output1 = f"Step:  {self.step_time:.4f}       Drawing: {self.draw_time:.4f}"
        output2 = f"Space: {self.simulation.space_time:.4f}      Goopie: {self.simulation.goopie_time:.4f}"
        output3 = f"Best:  {self.simulation.best_fitness:.4f}      Last:   {last_fitness}"
        arcade.draw_text(output1, -self.simulation.space_size + 20, self.simulation.space_size - 60, arcade.color.WHITE, 50)
        arcade.draw_text(output2, -self.simulation.space_size + 20, self.simulation.space_size - 120, arcade.color.WHITE, 50)
        arcade.draw_text(output3, -self.simulation.space_size + 20, self.simulation.space_size - 180, arcade.color.WHITE, 50)
        self.draw_time = timeit.default_timer() - draw_start_time

    def on_update(self, delta_time: float):
        step_start_time = timeit.default_timer()

        self.simulation.step()

        if not self.headless:
            self.update_sprites()

        self.frame += 1
        if self.frame % 1000 == 0:
            print("frames:", self.frame)
        
        self.step_time = timeit.default_timer() - step_start_time

        
    def update_sprites(self):
        for goopie in self.simulation.goopies:
            pos = goopie.get_position()
            goopie.sprite.set_position(*pos)
            goopie.sprite.angle = degrees(goopie.shape.body.angle - pi/2) 
        
        for food in self.simulation.foods:
            pos = food.get_position()
            food.sprite.set_position(*pos)
            food.sprite.angle = degrees(food.shape.body.angle - pi/2)