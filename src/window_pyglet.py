import timeit
from math import degrees, pi
import pyglet
from pyglet import app
from pyglet.window import Window
from camera_group import CenteredCameraGroup
from goopie import Goopie
from food import Food
from simulation import Simulation


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
WINDOW_TITLE = "GOOPIES SIMULATION"

GOOPIE_IMAGE_SIZE = 460
FOOD_IMAGE_SIZE = 460

class GameWindow(Window):
    def __init__(self, simulation: Simulation, width:int = SCREEN_WIDTH, height:int = SCREEN_HEIGHT, title:str=WINDOW_TITLE):
        super().__init__(width=width, height=height, caption=title)
        pyglet.gl.glClearColor(0, 0, 0, 0)
        self.set_location(400, 200)
        
        self.camera = CenteredCameraGroup(self, 0, 0, 0.45)


        self.food_img = pyglet.image.load("./sprites/food.png")
        self.goopie_img = pyglet.image.load("./sprites/goopie.png")
        self.goopie_img.anchor_x = self.goopie_img.width // 2
        self.goopie_img.anchor_y = self.goopie_img.height // 2
        self.food_img.anchor_x = self.food_img.width // 2
        self.food_img.anchor_y = self.food_img.height // 2
        self.set_icon(self.goopie_img)

        self.goopie_sprites = pyglet.graphics.Batch()
        self.goopie_vision_arcs_batch = pyglet.graphics.Batch()
        for goopie in simulation.goopies:
            self.add_goopie_sprite(goopie)


        self.food_sprites = pyglet.graphics.Batch()
        for food in simulation.foods:
            self.add_food_sprite(food)

        self.wall_lines = pyglet.graphics.Batch()
        self.walls = []
        for wall in simulation.walls:
            w = pyglet.shapes.Line(wall.a.x, wall.a.y, wall.b.x, wall.b.y, width=20, color=[255, 255, 255, 255], batch=self.wall_lines, group=self.camera)
            self.walls.append(w)
        
        self.simulation = simulation
        self.draw_time = 0
        self.frame = 0
        self.headless = False

    def add_goopie_sprite(self, goopie: Goopie):
        scale = 2 * goopie.RADIUS / GOOPIE_IMAGE_SIZE
        sprite = pyglet.sprite.Sprite(self.goopie_img, batch=self.goopie_sprites, group=self.camera)
        sprite.scale = scale
        x, y = goopie.get_position()
        sprite.position = (x, y, 0)
        goopie.set_sprite(sprite)

        vision_arc = pyglet.shapes.Arc(x, y, radius=goopie.VISION_RADIUS, thickness=1, batch=self.goopie_vision_arcs_batch, group=self.camera)
        goopie.vision_arc = vision_arc
        

    def add_food_sprite(self, food: Food):
        scale = 2 * food.RADIUS / GOOPIE_IMAGE_SIZE
        
        sprite = pyglet.sprite.Sprite(self.food_img, batch=self.food_sprites, group=self.camera)
        sprite.scale = scale
        x, y = food.get_position()
        sprite.position = (x, y, 0)
        food.set_sprite(sprite)

    def run(self):
        app.run()

    def on_draw(self):

        self.simulation.step()
        self.update_sprites()


        self.clear()            

        draw_start_time = timeit.default_timer()
        # arcade.start_render()

        self.goopie_sprites.draw()
        self.food_sprites.draw()

        # vision shape
        self.goopie_vision_arcs_batch.draw()
        
        # draw walls
        self.wall_lines.draw()
        
        last_fitness = 0
        # if len(self.simulation.best_goopies) > 0:
        #     last_fitness = self.simulation.best_goopies[-1].fitness
        # output1 = f"Step:  {self.step_time:.4f}       Drawing: {self.draw_time:.4f}"
        # output2 = f"Space: {self.simulation.space_time:.4f}      Goopie: {self.simulation.goopie_time:.4f}"
        # output3 = f"Best:  {self.simulation.best_fitness:.4f}      Last:   {last_fitness}"
        # arcade.draw_text(output1, -self.simulation.space_size + 20, self.simulation.space_size - 120, arcade.color.WHITE, 100)
        # arcade.draw_text(output2, -self.simulation.space_size + 20, self.simulation.space_size - 240, arcade.color.WHITE, 100)
        # arcade.draw_text(output3, -self.simulation.space_size + 20, self.simulation.space_size - 360, arcade.color.WHITE, 100)
        self.draw_time = timeit.default_timer() - draw_start_time

    def update_sprites(self):
        for goopie in self.simulation.goopies:
            # update goopie sprite
            pos = goopie.get_position()
            goopie.sprite.position = pos.x, pos.y, 0
            goopie.sprite.rotation = -degrees(goopie.shape.body.angle - pi/2) 
            # update vision arc
            goopie.vision_arc.position = pos.x, pos.y

        
        for food in self.simulation.foods:
            pos = food.get_position()
            food.sprite.position = pos.x, pos.y, 0
            food.sprite.rotation = -degrees(food.shape.body.angle - pi/2)

if __name__ == "__main__":
    window = GameWindow()
    app.run()