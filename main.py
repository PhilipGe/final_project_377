from kivy.graphics import *
from kivy.app import App
from kivy.uix.widget import Widget    
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from random import randrange

RED = (1,0,0,1)
LGR = (0,0.3,0,1)
GRN = (0,0.2,0,1)
BLU = (0,0,1,1)
WHT = (1,1,1,1)

#__________Fundamental Data Structures_____________
class Variable:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def to_string(self):
        return self.name + " " + str(self.size)

class Page:
    
    def __init__(self, id, size=32):
        self.id = id
        self.size = size
        self.used_size = 0
        self.variables = []
        self.highlight = False

    def add_variable(self, variable: Variable):
        self.variables.append(variable)
        self.used_size += variable.size

    def sync_page(self, page):
        if(self.id != page.id):
            raise Exception("Page IDs should be the same")

        self.used_size = page.used_size
        self.variables = page.variables
    
#The state of a single UI 'Stack' is described using this class
class StackState:

    def __init__(self, address_space_size, size_of_page, randomize_pages=False, cache = False):
        self.cache = cache

        if(address_space_size % size_of_page != 0):
            raise Exception("Invalid (address_space_size \% size_of_page) != 0")
        
        self.number_of_pages = int(address_space_size / size_of_page)

        if(not randomize_pages):
            self.pages = [Page(page_id, size_of_page) for page_id in range(self.number_of_pages-1, -1,-1)]
            if(cache):
                self.full = False
                self.page_queue = [p.id for p in self.pages]
        else:
            self.pages = []
            id_list = [i for i in range(self.number_of_pages)]
            while(len(id_list) != 0):
                i = randrange(0,len(id_list))
                self.pages.append(Page(id_list[i]))
                id_list.pop(i)

    def get_page_with_id(self, id):
        for page in self.pages:
            if(page.id == id):
                return page
        
        return -1
        
    def update_page(self, updated_page: Page):
        curr_page = self.get_page_with_id(updated_page.id)
        curr_page.sync_page(updated_page)

    def update_queue(self, id_just_visited):
        while(True):
            try:
                self.page_queue.remove(id_just_visited)
            except ValueError:
                break

        self.page_queue.append(id_just_visited)

    #Caching to allow for page completion
    def get_page_from_disk(self, page_id, stack, disk):
        if(not self.cache):
            return
        
        drop_id = self.page_queue[0]
        for p_ind in range(len(self.pages)):
            if(drop_id == self.pages[p_ind].id):
                drop_index = p_ind
                break
        
        #Replace page in cache
        incoming_page = stack.get_page_with_id(page_id)
        
        #Get actual page that is leaving cache
        leaving_page = self.pages[drop_index]

        #Save leaving page onto disk
        disk.update_page(leaving_page)
        disk.update_page(Page(page_id))

        #Load incoming page into cache
        self.pages[drop_index] = Page(incoming_page.id, incoming_page.size)
        self.pages[drop_index].sync_page(incoming_page)

        #Update Least Recently Accessed queue
        incoming_id = incoming_page.id
        self.update_queue(incoming_id)
        self.page_queue.pop(0)


    def add_variable(self, page_id, variable: Variable, stack = None, disk = None):
        page = self.get_page_with_id(page_id)

        #If we reach this point - page not found - that means we are in the cache stack
        if(page == -1):
            self.get_page_from_disk(page_id,stack,disk)

        else:
            if(not self.cache):
                page.add_variable(variable)
            else:
                page.sync_page(stack.get_page_with_id(page_id))
                self.update_queue(page.id)

    def save_variable(self, variable: Variable, heap=False):

        #Determine what part of memory to place object in
        iter_range = range(len(self.pages)-1,-1,-1) if not heap else range(len(self.pages))
        id = -1

        #Find first page in memory that has space
        for p_index in iter_range:
            page = self.pages[p_index]
            if(page.size - page.used_size >= variable.size):
                id = page.id
                break
        
        if(id == -1):
            return -1

        self.add_variable(id, variable)

        return id
    
    def find_variables_page(self, var_name):
        for page in self.pages:
            for v in page.variables:
                if(v.name == var_name):
                    return page
                
        return -1

#A 'Stack' in the UI sense is a column of rectangles
class StackUI:
    class RectDescriptor:
        def __init__(self, pos, size, text, variable_names, color = (1,1,1,1), highlight = False):
            self.pos = pos
            self.size = size
            self.color = color
            self.text = text
            self.variable_names = variable_names
            
    
    def __init__(self, fractional_size, fractional_position, state: StackState):
        self.width_fraction = fractional_size[0]
        self.total_height_fraction = fractional_size[1]
        self.fractional_position_x = fractional_position[0]
        self.fractional_position_y = fractional_position[1]
        self.state = state
        
    def update_values(self, window_size):
        self.size = window_size
        self.late_initialization()

    def late_initialization(self):
        width = self.size[0]
        height = self.size[1]
        self.total_height = height*self.total_height_fraction
        self.width = width * self.width_fraction
        self.position = (width*self.fractional_position_x, height*self.fractional_position_y)
    
        self.cell_height = self.total_height/self.state.number_of_pages

        #Set up descriptions of rectangles to draw
        self.rectangle_descriptors = []
        for page_id in range(self.state.number_of_pages):
            if(self.state.pages[page_id].highlight):
                color = LGR
            elif(self.state.pages[page_id].used_size != 0):
                color = GRN
            else:
                color = WHT

            self.state.pages[page_id].highlight = False
            self.rectangle_descriptors.append(
                self.RectDescriptor(
                    pos=(self.position[0],self.position[1] + page_id*(self.cell_height)), 
                    size=(self.width, self.cell_height-1),
                    color=color,
                    text= str(self.state.pages[page_id].id),
                    variable_names=[v.to_string() for v in self.state.pages[page_id].variables],
                )
            )


        
class MainCanvas(Widget):

    def __init__(self, **kwargs):
        super(MainCanvas, self).__init__(**kwargs)
        self.file_loaded = False

        page_size = 32

        address_space_size = page_size*8
        
        cache_size = page_size*3

        self.stack_state = StackState(address_space_size, page_size)
        self.disk_state = StackState(address_space_size, page_size, randomize_pages=True)
        self.cache_state = StackState(cache_size, page_size, cache=True)

        large_stack_height = 0.8
        small_stack_height = 0.8*(cache_size/address_space_size)
        
        self.stack_ui = StackUI((0.1,large_stack_height), (0.1,0.1), self.stack_state)
        self.cache_ui = StackUI((0.1,small_stack_height), (0.4,0.3), self.cache_state)
        self.disk_ui = StackUI((0.1,large_stack_height), (0.7,0.1), self.disk_state)

        self.uis = [self.stack_ui, self.cache_ui, self.disk_ui]

        self.labels = []
    
    #____________________________UI Details________________________________
    def draw_stacks(self):
        self.canvas.clear()
        self.clear_widgets()

        input_width = Window.width*0.2
        input_height = Window.height*0.1
        x_pos = (Window.width - input_width*1.5)/2
        y_pos = Window.height *0.05

        # Create a text input widget
        self.text_input = TextInput(multiline=False)
        self.text_input.bind(on_text_validate=self.on_enter)
        self.text_input.pos = (x_pos, y_pos)
        self.text_input.size = (input_width, input_height)

        # Add the text input widget to the layout
        self.add_widget(self.text_input)

        for ui in self.uis:
            self.draw_a_stack(ui)

    def draw_a_stack(self, stack_ui):
        with self.canvas:
            for rect_desc in stack_ui.rectangle_descriptors:
                Color(*rect_desc.color)
                Rectangle(pos=rect_desc.pos, size=rect_desc.size)
                
        for rect_desc in stack_ui.rectangle_descriptors:
            l = Label(text=rect_desc.text, pos=rect_desc.pos, text_size=(rect_desc.size[0]+Window.width*0.13,rect_desc.size[1]), halign="right", valign="top", font_size=80, 
                      color=(0,0,0,1) if rect_desc.color == WHT else WHT
                      )
            self.add_widget(l)
            name_list = "" if len(rect_desc.variable_names) == 0 else '   {:16s} '.format(rect_desc.variable_names[0])

            m = 0
            for n_i in range(1, len(rect_desc.variable_names)):
                name = rect_desc.variable_names[n_i]
                if(m % 2 == 0):
                    name_list += name
                else:
                    name_list += "\n" + '   {:16s} '.format(name)
                m += 1
                
            name_pos = (rect_desc.pos[0] + rect_desc.size[0]/3, rect_desc.pos[1]+Window.height*0.05)
 
            l2 = Label(text=name_list, pos=name_pos,  font_size=30, text_size = rect_desc.size, halign='left', valign='bottom')
            self.add_widget(l2)

    def on_size(self, canvas, observables):
        width = Window.width
        height = Window.height

        #Update the heights of each 'stack'
        for ui in self.uis:
            ui.update_values((width, height))

        self.draw_stacks()

    #__________________Command Executions_______________________
    def save_variable(self, name: str, size, heap=False):
        if(self.get_variable(name, verbose=False) != -1):
            print("Error: variable already exists")
            return
        
        page_id = self.stack_state.save_variable(Variable(name, size),heap=heap)
        
        if(page_id == -1): #Memory is full
            print("Not enough memory for variable of that size")
            return -1
        self.cache_state.add_variable(page_id, Variable(name, size), stack=self.stack_state, disk=self.disk_state)

        self.draw_stacks()
        return 0
    
    def highlight_page(self, page_id):
        self.stack_state.get_page_with_id(page_id).highlight = True
        self.cache_state.get_page_with_id(page_id).highlight = True
    
    def get_variable(self, var_name, verbose = True):
        page = self.stack_state.find_variables_page(var_name)
        if(page == -1):
            if(verbose):
                print("Variable '" + var_name + "' not found")
            return -1
        page_in_cache = self.cache_state.get_page_with_id(page.id) != -1

        if(page_in_cache):
            self.cache_state.update_queue(page.id)
        else:
            self.cache_state.get_page_from_disk(page.id, self.stack_state, self.disk_state)
        
        self.highlight_page(page.id)

    #____________________Interpeter______________________
    def execute_command(self, arr):
        print(arr)
        if(arr[0] == ''):
            return
        
        commands = ["get", "heap", "stack", "load"]
        if(arr[0].lower() not in commands):
            print("Error: " + arr[0] + " is not a command")
            self.text_input.text = ''
            return
        
        while True:
            try:
                arr.remove('')
            except ValueError:
                break

        if(arr[0].lower() == "get"):
            if(len(arr) != 2):
                print("Error: the GET commands takes one argument: GET VAR_NAME")
            self.get_variable(arr[1])
        
        elif(arr[0].lower() == "heap"):
            if(len(arr) != 3):
                print("Error: the HEAP command takes two arguments: HEAP VAR_NAME SIZE")
            self.save_variable(arr[1],int(arr[2]),heap=True)
        
        elif(arr[0].lower() == "stack"):
            if(len(arr) != 3):
                print("Error: the STACK command takes two arguments: STACK VAR_NAME SIZE")
            self.save_variable(arr[1],int(arr[2]),heap=False)
        
        elif(arr[0].lower() == "load"):
            if(len(arr) != 2):
                print("Error: the LOAD command takes two arguments: LOAD FILENAME")
            self.execute_file(arr[1])

    def execute_file(self, filename):
        try:
            with open(filename) as f:
                arr = f.readlines()
        
            for line in arr:
                self.execute_command([e.strip() for e in line.split(" ")])
        
        except:
            print("File " + filename + " not found")
    
    def on_enter(self, instance):
        # Retrieve the user's input
        user_input = self.text_input.text

        arr = user_input.split(" ")
        self.execute_command(arr)

        self.text_input.text = ''
        self.on_size(0,0)

class MyApp(App):
    def build(self):
        return MainCanvas()

if __name__ == "__main__":
    MyApp().run()