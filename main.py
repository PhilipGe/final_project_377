from kivy.graphics import *
from kivy.app import App
from kivy.uix.widget import Widget    
from kivy.core.window import Window
from kivy.uix.label import Label
    
class StackState:
    def __init__(self, address_space_size, size_of_page):
        if(address_space_size % size_of_page != 0):
            raise Exception("Invalid (address_space_size \% size_of_page) != 0")
        
        self.number_of_pages = int(address_space_size / size_of_page)
        self.page_in_use = [False for page in range(self.number_of_pages)]
        self.page_label = ["" for page in range(self.number_of_pages)]

class StackUI:
    class RectDescriptor:
        def __init__(self, pos, size, number = -1,  color = (1,1,1,1)):
            self.pos = pos
            self.size = size
            self.color = color
            self.number = number
            self.label = Label(text=str(number), pos=pos, size=size, halign="center", valign="middle", color=(0,0,0,1))
    
    def __init__(self, fractional_size, fractional_position, state: StackState):
        self.width_fraction = fractional_size[0]
        self.total_height_fraction = fractional_size[1]
        self.fractional_position_x = fractional_position[0]
        self.fractional_position_y = fractional_position[1]
        self.state = state
        
    def update_values(self, window_size):
        self.size = window_size

        self.late_initialization(window_size)

    def late_initialization(self, size):
        width = size[0]
        height = size[1]
        self.total_height = height*self.total_height_fraction
        self.width = width * self.width_fraction
        self.position = (width*self.fractional_position_x, height*self.fractional_position_y)
    
        self.cell_height = self.total_height/self.state.number_of_pages

        #Set up descriptions of rectangles to draw
        self.rectangle_descriptors = [self.RectDescriptor(

            pos=(self.position[0],self.position[1] + y_index*(self.cell_height+4)), \
            size=(self.width, self.cell_height)        

              ) for y_index in range(self.state.number_of_pages)]
        
class MainCanvas(Widget):

    def __init__(self, **kwargs):
        super(MainCanvas, self).__init__(**kwargs)
        self.toggle = False

        address_space_size = 32
        page_size = 4

        cache_size = 12

        self.stack_state = StackState(address_space_size, page_size)
        self.disk_state = StackState(address_space_size, page_size)
        self.cache_state = StackState(cache_size, page_size)

        large_stack_height = 0.8
        small_stack_height = 0.8*(cache_size/address_space_size)
        
        self.stack_ui = StackUI((0.1,large_stack_height), (0.1,0.1), self.stack_state)
        self.cache_ui = StackUI((0.1,small_stack_height), (0.4,0.3), self.cache_state)
        self.disk_ui = StackUI((0.1,large_stack_height), (0.7,0.1), self.disk_state)

        self.uis = [self.stack_ui, self.cache_ui, self.disk_ui]
    
    def draw_stacks(self):
        self.canvas.clear()

        for ui in self.uis:
            self.draw_a_stack(ui)

    def draw_a_stack(self, stack_ui):
        with self.canvas:
            for rect_desc in stack_ui.rectangle_descriptors:
                Color(*rect_desc.color)
                Rectangle(pos=rect_desc.pos, size=rect_desc.size)
                if(rect_desc.number >= 0):
                    self.add_widget(rect_desc.label)

    def on_size(self, canvas, observables):
        width = Window.width
        height = Window.height

        #Update the heights of each 'stack'
        for ui in self.uis:
            ui.update_values((width, height))

        self.draw_stacks()

    # def color_one_rectangle(self, ui, index, number):
        
        
        

    def update_canvas_on_resize(self):
        #TODO. Change the width and the height of the stacks
        pass
    
    # def on_touch_down(self, touch):
    #     print("Touch!")
    #     self.draw_stacks()
        
    #     return super().on_touch_down(touch)

    

class MyApp(App):

    def build(self):

        return MainCanvas()

if __name__ == "__main__":
    MyApp().run()