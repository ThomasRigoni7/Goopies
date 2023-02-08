import arcade
import timeit
from simulation import Simulation
from math import degrees
from pymunk.pyglet_util import DrawOptions

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WINDOW_TITLE = "GOOPIES SIMULATION"

class GameWindow(arcade.Window):
    def __init__(self, simulation: Simulation, update_rate: float = 1/60):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, update_rate=update_rate)
        self.set_location(400, 200)
        self.background_color = arcade.color.DARK_SLATE_GRAY
        self.simulation = simulation

        self.options = DrawOptions()

        self.camera = arcade.Camera()
        screen_center_x = - self.camera.viewport_width / 2
        screen_center_y = - self.camera.viewport_height / 2
        camera_center = screen_center_x, screen_center_y
        self.camera.move_to(camera_center)

        self.goopie_sprites = arcade.SpriteList()
        for goopie in simulation.goopies:
            sprite = arcade.Sprite("./sprites/goopie.png")
            print(sprite.width)
            print(sprite.height)
            x, y = goopie.get_position()
            sprite.set_position(x, y)
            goopie.set_sprite(sprite)
            self.goopie_sprites.append(sprite)
        self.draw_time = 0

    def on_draw(self):
        if self.headless:
            return
        
        self.clear()
        self.camera.use()

        draw_start_time = timeit.default_timer()
        arcade.start_render()

        # self.goopie_sprites.draw()
        self.simulation.space.debug_draw(self.options)

        output = f"Drawing time: {self.draw_time:.5f} seconds per frame."
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)
        self.draw_time = timeit.default_timer() - draw_start_time

    def on_update(self, delta_time: float):
        self.simulation.step()
        # print(delta_time)
        if not self.headless:
            self.update_goopie_sprites()

    def update_goopie_sprites(self):
        for goopie in self.simulation.goopies:
            pos = goopie.get_position()
            goopie.sprite.set_position(*pos)
            goopie.sprite.angle = degrees(goopie.shape.body.angle)