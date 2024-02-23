import serial
import tkinter as tk
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import pyplot as plt
import numpy as np

#generate and plot the graph
def plot(x_coord, y_coord):
    global pathX
    global pathY

    # the figure that will contain the plot
    fig = Figure(figsize=(8, 8), dpi=100)

    # adding the subplot
    plot1 = fig.add_subplot(111)

    #set limits for graphs
    plot1.set_xlim([-300, 300])
    plot1.set_ylim([-300, 300])
    plot1.grid()

    plot1.plot(x_coord, y_coord, marker="o", markersize=10 )

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=RightFrame)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().place(relx = 0, rely = 0)

def startupPlot():
    global pathX
    global pathY

    # the figure that will contain the plot
    fig = Figure(figsize=(8, 8), dpi=100)

    # adding the subplot
    plot1 = fig.add_subplot(111)

    # set limits for graphs
    plot1.set_xlim([-300, 300])
    plot1.set_ylim([-300, 300])
    plot1.grid()

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=RightFrame)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().place(relx=0, rely=0)

#normalize angle between 0 and 2*pi
def NormalizeAngle(angle):
    if angle > 2*np.pi:
        solution = angle - abs(np.floor(angle / (2*np.pi)) * 2 * np.pi)
    elif angle < 0:
        solution = angle + abs(np.floor(angle / (2*np.pi)) * 2 * np.pi)
    else:
        solution = angle
    return solution

def StartPathFollow():
    global pathX
    global pathY

    for i in range(len(pathX)):
        set_coordinates_state(pathX[i], pathY[i])
        time.sleep(.5)

#when update button is pressed--> take entered coordinates and caclulate new coordinates, then update graph, then send to serial
def set_coordinates_state(x_coord, y_coord):

    plot(x_coord, y_coord)

    #send serial data to arduino
    ser.write(bytes( str(x_coord), 'UTF-8'))
    ser.write(bytes('A', 'UTF-8'))
    ser.write(bytes( str(y_coord-90), 'UTF-8'))
    ser.write(bytes('B', 'UTF-8'))

#set path defaults
ActivePath=0;
pathX = [5, 5, 5, 5, 5, 5, 3, 1, -1, -3, -5, -5, -5, -5, -5, -5, -3, -1, 1, 3, 5]
pathY = [-5, -3, -1, 1, 3, 5, 5, 5, 5, 5, 5, 3, 1, -1, -3, -5, -5, -5, -5, -5, -5]
def ChangeSelectPathButton():
    global ActivePath
    global pathX
    global pathY
    global L1
    global L2

    numCases = 4

    if ActivePath >= numCases-1:
        ActivePath=0
    else:
        ActivePath=ActivePath+1

    # match ActivePath:
    #     case 0: #rectangle
    #         pathX = [ 5,  5,  5, 5, 5, 5, 3, 1, -1, -3, -5 , -5 , -5, -5, -5 , -5, -3, -1, 1, 3, 5]
    #         pathY = [-5, -3, -1, 1, 3, 5, 5, 5 , 5,  5,  5,   3,   1, -1, -3,  -5, -5, -5,-5,-5,-5]
    #     case 1: #involute of circle
    #         u = np.linspace(0, 6.5 * np.pi, 150)
    #         c = .45
    #         pathX = (c * (np.cos(u) + u * np.sin(u)))
    #         pathY = c * (np.sin(u) - u * np.cos(u))
    #     case 2:  # Heart
    #         u = np.linspace(0,  2 * np.pi, 100)
    #         c = .3
    #         pathX = (6*c*np.sin(u))**3
    #         pathY = 13*c*np.cos(u)-5*c*np.cos(2*u)-2*c*np.cos(3*u)-c*np.cos(4*u)
    #     case 3:  # lemniscate
    #         u = np.linspace(0, 2 * np.pi, 50)
    #         c = 5
    #         pathX = (c * np.cos(u))
    #         pathY = c * np.sin(2 * u)
    #     case default: #rectangle
    #         pathX = [ 5,  5,  5, 5, 5, 5, 3, 1, -1, -3, -5 , -5 , -5, -5, -5 , -5, -3, -1, 1, 3, 5]
    #         pathY = [-5, -3, -1, 1, 3, 5, 5, 5 , 5,  5,  5,   3,   1, -1, -3,  -5, -5, -5,-5,-5,-5]

    startupPlot(L1, L2)

#set up serial comms--------------------------------------------------------------------------------------------------------------------------------------------------
ser = serial.Serial('com3', 9600) #create Serial Object
time.sleep(3) #delay 3 seconds to allow serial com to get established

# Build GUI------------------------------------------------------------------------------------------------------------------------------------------------------------
tkTop = tk.Tk()  # Create GUI Box
tkTop.geometry('1200x800')  # size of GUI
tkTop.title("2 DOF GUI")  # title in top left of window

Title = tk.Label(text='Enter the desired coordinates of the Rig', font=("Courier", 14, 'bold')).pack()  # Title on top middle of screen

# Fill in the left Side------------------------------------------------------------------------------------------------
leftFrame = tk.Frame(master=tkTop, width=600) # create frame for the entry controls

leftFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

TextFrame = tk.Frame(master=leftFrame, width=100)
x_input_Lable = tk.Label(master=TextFrame, text='X Coordinate:',
                                 font=("Courier", 12, 'bold')).pack(side='top', ipadx=0, padx=0, pady=0)
y_input_Lable = tk.Label(master=TextFrame, text='Y Coordinate:',
                                 font=("Courier", 12, 'bold')).pack(side='top', ipadx=0, padx=0, pady=0)

EntryFrame = tk.Frame(master=leftFrame, width=100)

x_coord_entry = tk.Entry(EntryFrame)
x_coord_entry.pack(side='top', ipadx=0, padx=0, pady=0)

y_coord_entry = tk.Entry(EntryFrame)
y_coord_entry.pack(side='top', ipadx=0, padx=0, pady=0)

#set intial coords to zero.
x_coord_entry.insert(0,0)
y_coord_entry.insert(0,0)

UpdateCoordsButton = tk.Button(EntryFrame,
                                   text="Update Coordinates",
                                   command=lambda:set_coordinates_state(float(x_coord_entry.get()),float(y_coord_entry.get())),
                                   height=4,
                                   fg="black",
                                   width=20,
                                   bd=5,
                                   activebackground='green'
                                   )
UpdateCoordsButton.pack(side='top', ipadx=10, padx=10, pady=40)

StartPathButton = tk.Button(EntryFrame,
                                   text="Follow Path",
                                   command=StartPathFollow,
                                   height=4,
                                   fg="black",
                                   width=20,
                                   bd=5,
                                   activebackground='green'
                                   )
StartPathButton.pack(side='top', ipadx=10, padx=10, pady=40)

PathSelectorButton = tk.Button(EntryFrame,
                                   text="Change Path",
                                   command=ChangeSelectPathButton,
                                   height=4,
                                   fg="black",
                                   width=20,
                                   bd=5,
                                   activebackground='green'
                                   )
PathSelectorButton.pack(side='top', ipadx=10, padx=10, pady=40)

TextFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
EntryFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

# Fill in the right Side of GUI----------------------------------------------------------------------------------------
RightFrame = tk.Frame(master=tkTop, width=600, bg="gray")


RightFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
startupPlot()

tk.mainloop() # run loop watching for gui interactions