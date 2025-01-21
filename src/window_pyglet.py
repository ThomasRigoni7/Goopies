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
        self.set_location(900, 200)
        
        zoom = 500 / simulation.space_size

        self.camera = CenteredCameraGroup(self, 0, 0, zoom)


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
        self.step_time = None

    def add_goopie_sprite(self, goopie: Goopie):
        scale = 2 * goopie.RADIUS / GOOPIE_IMAGE_SIZE
        sprite = pyglet.sprite.Sprite(self.goopie_img, batch=self.goopie_sprites, group=self.camera)
        sprite.scale = scale
        x, y = goopie.get_position()
        sprite.position = (x, y, 0)
        goopie.set_sprite(sprite)

        vision_arc = pyglet.shapes.Arc(x, y, radius=goopie.vision.VISION_RADIUS, thickness=1, batch=self.goopie_vision_arcs_batch, group=self.camera)
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

        step_start_time = timeit.default_timer()
        self.simulation.step()
        self.step_time = timeit.default_timer() - step_start_time
        self.update_sprites()


        self.clear()

        draw_start_time = timeit.default_timer()

        self.goopie_sprites.draw()
        self.food_sprites.draw()

        # vision shape
        self.goopie_vision_arcs_batch.draw()
        
        # draw walls
        self.wall_lines.draw()
        
        if False:
            # show vision of first goopie
            from goopie import VisionGoopie
            g : VisionGoopie = self.simulation.goopies[0]
            vision = (g.visual_buffer * 255).byte().numpy()
            import numpy as np
            vision = np.dstack([vision, vision, vision]) * 255
            pixels = vision.flatten().tolist()
            from pyglet.gl import GLubyte
            rawData = (GLubyte * len(pixels))(*pixels)
            imageData = pyglet.image.ImageData(10, 3, 'RGB', rawData)
            rect = pyglet.shapes.Rectangle(690, 30, 120, 50)
            rect.draw()
            imageData.blit(700, 40, width=100, height=30)

        # pyglet.text.Label(f"Age: {self.simulation.goopies[0].age}", 20, 80, color=[255, 255, 255], height=100).draw()

        # show stats
        last_fitness = 0
        if len(self.simulation.best_goopies) > 0:
            last_fitness = self.simulation.best_goopies[-1].fitness
        # output1 = f"Step:  {self.step_time:.4f}       Drawing: {self.draw_time:.4f}"
        # output2 = f"Space: {self.simulation.space_time:.4f}      Goopie: {self.simulation.goopie_time:.4f}"
        output2 = f"FPS: {(1 / (self.step_time + self.draw_time)):.1f}"
        output3 = f"Best:  {self.simulation.best_fitness:.4f}      Last:   {last_fitness}"
        # pyglet.text.Label(output1, 20, 60, color=[255, 255, 255], height=100).draw()
        pyglet.text.Label(output2, 20, 40, color=[255, 255, 255], height=100).draw()
        pyglet.text.Label(output3, 20, 20, color=[255, 255, 255], height=100).draw()
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
        
    def save_a_frame(self):
        file_num=str(self.simulation.num_steps - 2000).zfill(5)
        filename="frames/frame-"+file_num+'.png'
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
        print('image file writen : ',filename)

if __name__ == "__main__":
    window = GameWindow()
    app.run()