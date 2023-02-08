import arcade
import timeit
from simulation import Simulation
from math import degrees
from goopie import Goopie
import pyglet
import time

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
WINDOW_TITLE = "GOOPIES SIMULATION"

GOOPIE_IMAGE_SIZE = 460
FOOD_IMAGE_SIZE = ...

class GameWindow(arcade.Window):
    def __init__(self, simulation: Simulation, update_rate: float = 1/60):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, update_rate=update_rate)
        self.set_location(400, 200)
        self.background_color = arcade.color.DARK_SLATE_GRAY
        self.simulation = simulation

        # compute scale for sprites
        self.goopie_scale = 2 * Goopie.RADIUS / GOOPIE_IMAGE_SIZE


        
        self.camera = arcade.Camera()
        P = pyglet.math.Mat4.orthogonal_projection(-simulation.space_size, simulation.space_size, -simulation.space_size, simulation.space_size, -255, 255)
        print(P)
        self.camera.projection_matrix = P

        self.goopie_sprites = arcade.SpriteList()
        for goopie in simulation.goopies:
            sprite = arcade.Sprite("./sprites/goopie.png", self.goopie_scale)
            x, y = goopie.get_position()
            sprite.set_position(x, y)
            goopie.set_sprite(sprite)
            self.goopie_sprites.append(sprite)
        self.draw_time = 0
        self.frame = 0

    def on_draw(self):
        if self.headless:
            return
        
        self.clear()
        self.camera.use()

        draw_start_time = timeit.default_timer()
        arcade.start_render()

        self.goopie_sprites.draw()

        output = f"Drawing time: {self.draw_time:.5f} seconds per frame."
        arcade.draw_text(output, -self.simulation.space_size + 20, self.simulation.space_size - 60, arcade.color.WHITE, 50)
        self.draw_time = timeit.default_timer() - draw_start_time

    def on_update(self, delta_time: float):
        self.simulation.step()

        if not self.headless:
            self.update_goopie_sprites()

        self.frame += 1

        
    def update_goopie_sprites(self):
        for goopie in self.simulation.goopies:
            pos = goopie.get_position()
            goopie.sprite.set_position(*pos)
            goopie.sprite.angle = degrees(goopie.shape.body.angle)