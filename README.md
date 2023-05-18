# Virtual Memory, Phyical Memory, and the Disk
One of the big appeals of virtual memory is the ability to allocate more memory to a process than is physically available. This is achieved by swapping pages of memory between physical memory and disk storage. This simulation visualizes that useful property of paging, letting the user interactively create new data and watch where that data is stored in the Virtual and Physical address spaces.

# First: Installing Kivy and Running Sim
Kivy is a cross-platform python graphics package. In this final project it was used to construct a simulation that describes the 
relationship between Virtual Memory, Physical Memory, and the Disk.

Preinstalled Dependencies Needed:
- Python3
- pip

Other dependency needed (instructions on on installing are below):
- Kivy

Before running the python file, you need to install Kivy. The installation is covered here:
    https://kivy.org/doc/stable/gettingstarted/installation.html#setup-terminal-and-pip

**IMPORTANT** Make sure to both install Kivy and run the virtual environment in the root directory of this repository (the place you ran "git clone" in.) These steps are covered on the page that opens from the link above.

If all went well you can run:

    > python3 main.py

to start the simulation. For the best experience, make the window that opens up full screen.

# Fundamental Data Structures
The three fundamental data structures, in reverse heirarchical order, are:
- Variable
- Page
- Stack

A variable is stored in a page, and a page is stored on a "stack". This stack is a purely practical structure that describes a number of pages "stacked" on top of each other. It is different from the stack we, programmers, are familiar with.

The vital data each holds is as follows
- Variable
    - Name
    - Size (bytes)
- Page
    - List of Variables
    - Size (bytes)
- Stack
    - List of Pages
    - Size (bytes)

The purpose of these structures is to create logical groups that will help us visualize the relationship between the virtual and physical address spaces. 

# Command Interface
In the simulation, you can run a limited set of commands to CREATE and GET variables. As you do so, you can watch their location in the virtual address space and the physical address spaces.

The commands you can run are as follows. The CREATE commands are:
    
    HEAP 
    STACK 

The other two commands are:

    GET 
    LOAD 

The HEAP and STACK commands both create variables with a NAME and SIZE. The STACK command places the variable in the top of the _virtual_ address space, while the HEAP command places it on the bottom. Variables are stored in even-sized pages, both in virtual and physical memory. When the following commands are ran, the first page the has enough space within it to house the variable is the page to which the variable is assigned. From then on, all of the variables in that page will move around memory together:

    HEAP NAME SIZE
    STACK NAME SIZE

    HEAP new_var 4  ->   Creates "new_var" of size 4 on heap

The location of a page in the physical address space is essentially random. Whenever a new variable is created, its location can be seen in both the physical and virtual address spaces shown in the simulation. 

The GET command can be run with a variable NAME as an argument. If the variable is not in the physical memory, the simulation shows how the page it is in is loaded into the physical memory from the disk, swapping with the Least Recently Used page. If the variable IS in the cache, the GET command still has the effect of reordering the LRU queue.

    GET NAME

The LOAD command let's you create an internall executable text file made up of the three commands above to streamline the process of filling the memory, so that its caching is easier to demonstrate:

    LOAD FILENAME

# Fin
With the knowledge above, you know what there is to know about this simulation. You can run 

    python main.py

And then, inside of the GUI, run

    LOAD commands.txt

To get started!