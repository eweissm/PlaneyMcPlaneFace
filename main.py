import serial
import tkinter as tk
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import pyplot as plt
import numpy as np
import scipy.optimize
import progressbar
import re
import math

FileName = r"C:\Users\Ericw\Desktop\topSecretedata.csv"

L1 = 10
L2 = 10
# calculate the angles using inverse kinematics
theta0 = [0, 0]
prevTheta1 = 0


def calculate_joint_angles(x, y, L1, L2):
    global theta0
    global ErrorFlag
    global counter
    global prevTheta1  # previous solution to theta1

    counter = 0
    ErrorFlag = True

    while ErrorFlag and counter<5:

        solution,infodict, ier, msg = scipy.optimize.fsolve(func, theta0, args=(tuple((x, y, L1, L2))), full_output=1)

        # normalize angles
        solution[1] = NormalizeAngle(solution[1])

        if solution[1] > 3*np.pi/2 or solution[1] < np.pi/2 or ier != 1 or abs(solution[0]-prevTheta1) > 2*np.pi:

            counter = counter + 1
            rng = np.random.default_rng(12345)
            rFloat = np.pi*(rng.random(2)-.5)
            theta0 = [theta0[0]+rFloat[0], theta0[1]+rFloat[1]]

        else:
            ErrorFlag = False
            prevTheta1 = solution[0]


    if ErrorFlag:
        print("Error: Angles out of bounds")
        theta0 = [np.pi / 2, np.pi / 2]
    else:
        theta0 = solution

    return solution


# generate and plot the graph
def plot(x_coord, y_coord, theta, L1, L2):
    global pathX
    global pathY

    # the figure that will contain the plot
    fig = Figure(figsize=(8, 8), dpi=100)

    # adding the subplot
    plot1 = fig.add_subplot(111)

    # set limits for graphs
    plot1.set_xlim([-(L1+L2+2), (L1+L2+2)])
    plot1.set_ylim([-(L1+L2+2), (L1+L2+2)])
    plot1.grid()

    # plotting work space
    x, y = generate_semicircle(0, 0, np.sqrt(L1**2+L2**2), 0.01)
    plot1.plot(x, y, color='black', linestyle='dashed')
    plot1.plot(-x, y, color='black', linestyle='dashed')

    # plotting path
    plot1.plot(pathX, pathY, color='blue', linestyle='dashed')

    # plotting the arm
    plot1.plot(0, 0, marker="o", markersize=20)
    plot1.plot(x_coord, y_coord, marker="o", markersize=10)
    plot1.plot(L1*np.cos(theta[0]), L1*np.sin(theta[0]), marker="o", markersize=20)
    plot1.plot([0, L1*np.cos(theta[0])], [0, L1*np.sin(theta[0])])
    plot1.plot([L1 * np.cos(theta[0]), x_coord], [L1 * np.sin(theta[0]), y_coord])

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=RightFrame)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().place(relx=0, rely=0)


def GcodeConverter(fileName):
    x = []
    y = []

    with open(fileName, "r", encoding='utf-8-sig') as f:
        lines = f.read()
        lines2 = lines.splitlines()

        for line in lines2:
            match = re.search(r"X(\S*) Y(\S*)|X(\S*)|  Y(\S*)", line)

            if match != None:  # if we find a match
                result = match.groups()

                if result[0] != None:
                    x_temp = result[0]
                    y_temp = (result[1])

                    x.append(float(x_temp))
                    y.append(float(y_temp))
                elif result[2] != None:
                    x_temp = result[2]
                    y_temp = y[len(y) - 1]  # get last input

                    x.append(float(x_temp))
                    y.append(float(y_temp))
                elif result[3] != None:
                    y_temp = result[3]
                    x_temp = x[len(x) - 1]  # get last input

                    x.append(float(x_temp))
                    y.append(float(y_temp))

    return x, y


def startupPlot(L1, L2):
    global pathX
    global pathY

    # the figure that will contain the plot
    fig = Figure(figsize=(8, 8), dpi=100)

    # adding the subplot
    plot1 = fig.add_subplot(111)

    # set limits for graphs
    plot1.set_xlim([-(L1 + L2 + 2), (L1 + L2 + 2)])
    plot1.set_ylim([-(L1 + L2 + 2), (L1 + L2 + 2)])
    plot1.grid()

    # plotting work space
    x, y = generate_semicircle(0, 0, np.sqrt(L1**2+L2**2), 0.01)
    plot1.plot(x, y, color='black', linestyle='dashed')
    plot1.plot(-x, y, color='black', linestyle='dashed')

    # plotting path
    plot1.plot(pathX, pathY, color='blue', linestyle='dashed')

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=RightFrame)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().place(relx=0, rely=0)


# normalize angle between 0 and 2*pi
def NormalizeAngle(angle):
    if angle > 2*np.pi:
        solution = angle - abs(np.floor(angle / (2*np.pi)) * 2 * np.pi)
    elif angle < 0:
        solution = angle + abs(np.floor(angle / (2*np.pi)) * 2 * np.pi)
    else:
        solution = angle
    return solution


def generate_semicircle(center_x, center_y, radius, stepsize=0.1):
    """
    generates coordinates for a semicircle, centered at center_x, center_y
    """
    x = np.arange(center_x, center_x+radius+stepsize, stepsize)

    y = np.sqrt(abs(radius**2 - x**2))

    # since each x value has two corresponding y-values, duplicate x-axis.
    # [::-1] is required to have the correct order of elements for plt.plot.
    x = np.concatenate([x,x[::-1]])

    # concatenate y and flipped y.
    y = np.concatenate([y,-y[::-1]])

    return x, y + center_y


def StartPathFollow():
    global pathX
    global pathY

    set_coordinates_state(pathX, pathY)



prev_X_and_Y = [0,0]
# when update button is pressed--> take entered coordinates and calculate new coordinates, then update graph, then send
# to serial
def set_coordinates_state(x_coord, y_coord):
    global theta  # angles of joints 1 and 2
    global L1
    global L2
    global prev_X_and_Y  # Previous X and Y coordinates

    try:
        NumEntries = len(x_coord)
    # handle list / array case
    except TypeError:  # oops, was a float
        NumEntries = 1

    # define arm lengths
    L1 = 10
    L2 = 10

    theta1_deg = []
    theta2_deg = []

    ser.reset_input_buffer()  # clear input buffer

    # Pre-Calculate inverse Kinematics calculation
    print("Calculating Angles...")
    with progressbar.ProgressBar(max_value=NumEntries) as bar:
        for i in range(NumEntries):
            if NumEntries > 1:
                thisXCoord = x_coord[i]
                thisYCoord = y_coord[i]
            else:
                thisXCoord = x_coord
                thisYCoord = y_coord

            # In order to allow the arm to move in approximately straight lines between 2 points, we will discretize the
            # path taken between two point such that no 2 points along the path are greater than 1 cm

            #Length of straight line from current coords to target coords
            PathLength = np.sqrt((thisXCoord-prev_X_and_Y[0])**2 + (thisYCoord-prev_X_and_Y[1])**2)

            numberOfPathSteps = math.ceil(PathLength/1)

            # Find X and Y coordinates along the path
            if thisXCoord != prev_X_and_Y[0]:
                Xsteps = np.linspace(prev_X_and_Y[0], thisXCoord, numberOfPathSteps)
                if prev_X_and_Y[0] < thisXCoord:
                    Ysteps = np.interp(Xsteps, [prev_X_and_Y[0], thisXCoord], [prev_X_and_Y[1], thisYCoord])
                else:
                    Ysteps = np.interp(Xsteps, [thisXCoord, prev_X_and_Y[0]], [thisYCoord, prev_X_and_Y[1]])
            else:
                Ysteps = np.linspace(prev_X_and_Y[1], thisYCoord, numberOfPathSteps)
                if prev_X_and_Y[1] < thisYCoord:
                    Xsteps = np.interp(Ysteps, [prev_X_and_Y[1], thisYCoord], [prev_X_and_Y[0], thisXCoord])
                else:
                    Xsteps = np.interp(Ysteps, [thisYCoord, prev_X_and_Y[1]], [thisXCoord, prev_X_and_Y[0]])

            prev_X_and_Y = [thisXCoord, thisYCoord]  # update prev_X_and_Y

            for j in range(len(Xsteps)):


                theta = calculate_joint_angles(Xsteps[j], Ysteps[j], L1, L2)
                if not ErrorFlag:
                    # generate and plot the graph
                    plot(thisXCoord, thisYCoord, theta, L1, L2)
                    theta1_deg.append(int(theta[0] * 180 / np.pi))
                    theta2_deg.append(int(theta[1] * 180 / np.pi))
                else:
                    print("Failed to Calculate Coordinate: "+str(i))
                    break

            bar.update(i)

    print("Done Calculating Angles")


    # Run through the angles
    if not ErrorFlag:
        for i in range(len(theta1_deg)):

            start = time.time()

            # send serial data to arduino
            ser.write(bytes(str(theta1_deg[i]), 'UTF-8'))
            ser.write(bytes('A', 'UTF-8'))
            ser.write(bytes(str(theta2_deg[i]-90), 'UTF-8'))
            ser.write(bytes('B', 'UTF-8'))

            # get expected move time from arduino
            ExpectedTime_bytes = ser.readline()
            ExpectedTime_string = ExpectedTime_bytes.decode("utf-8")
            print("ExpectedTime: " + ExpectedTime_string)

            try:
                # convert expected time to float (minimum time is 0.005s)
                ExpectedTime = max(float(ExpectedTime_string), 0.1)
            except ValueError:
                ExpectedTime = 0.1

            ser.reset_input_buffer()  # clear input buffer

            # if we get a 'y' from arduino, we move on, otherwise we will wait 0.5 sec. We will repeat this 5 times.
            # After which, if we still do not have confirmation, we will print to the monitor that there was a problem
            # and move on

            DidMoveWork = False

            ArduinoMessage = ''

            MoveStartTime = time.time()

            while time.time()-MoveStartTime < ExpectedTime*4 and not DidMoveWork:
                if ser.inWaiting():
                    ArduinoMessage = ser.read(1)  # read one bit from buffer
                    #print(ArduinoMessage)

                if ArduinoMessage == b'y':
                    DidMoveWork = True
                    print("Move was successful")

            if not DidMoveWork:
                print("Move was not successful")

            ser.reset_input_buffer()  # clear input buffer
            end = time.time()
            print("Difference between expected time and actual time: " + str(end - start - ExpectedTime))


def func(angles, x, y, L1, L2):
    return [L1*np.cos(angles[0])+L2*(np.cos(angles[1])*np.cos(angles[0])-np.sin(angles[1])*np.sin(angles[0]))-x, L1*np.sin(angles[0])+L2*(np.cos(angles[1])*np.sin(angles[0])+np.sin(angles[1])*np.cos(angles[0]))-y]


# set path defaults
ActivePath = 0
pathX = [5, 5, 5, 5, 5, 5, 3, 1, -1, -3, -5, -5, -5, -5, -5, -5, -3, -1, 1, 3, 5]
pathY = [-5, -3, -1, 1, 3, 5, 5, 5, 5, 5, 5, 3, 1, -1, -3, -5, -5, -5, -5, -5, -5]


def ChangeSelectPathButton():
    global ActivePath
    global pathX
    global pathY
    global L1
    global L2

    numCases = 9

    if ActivePath >= numCases-1:
        ActivePath=0
    else:
        ActivePath=ActivePath+1

    match ActivePath:
        case 0:  # rectangle
            pathX = [ 5,  5,  5, 5, 5, 5, 3, 1, -1, -3, -5 , -5 , -5, -5, -5 , -5, -3, -1, 1, 3, 5]
            pathY = [-5, -3, -1, 1, 3, 5, 5, 5 , 5,  5,  5,   3,   1, -1, -3,  -5, -5, -5,-5,-5,-5]
        case 1:  # involute of circle
            u = np.linspace(0, 6.5 * np.pi, 150)
            c = .45
            pathX = (c * (np.cos(u) + u * np.sin(u)))
            pathY = (c * (np.sin(u) - u * np.cos(u)))
        case 2: # Heart
            u = np.linspace(0,  2 * np.pi, 100)
            c = .3
            pathX = (7*c*np.sin(u))**3
            pathY = (15*c*np.cos(u)-5*c*np.cos(2*u)-2*c*np.cos(3*u)-c*np.cos(4*u))*1.5
        case 3:  # lemniscate
            u = np.linspace(0, 2 * np.pi, 50)
            c = 5
            pathX = (c * np.cos(u))
            pathY = c * np.sin(2 * u)
        case 4:  # Lisajous curves
            u = np.linspace(0, 15 * np.pi, 400)
            pathX = (8 * np.sin(u*.9))
            pathY = 8 * np.sin(u)
        case 5:
            u = np.linspace(0, 2 * np.pi, 400)
            pathX = 7 * np.sin(7*u)
            pathY = 7 * np.cos(5*u)
        case 6: #Gcode input
            tempX, tempY = GcodeConverter(r"C:\Users\Ericw\Desktop\squareSpiral.gc")
            tempX = np.array(tempX)/15- 7.5
            tempY = np.array(tempY)/15 - 7.5

            pathX = tempX
            pathY = tempY
        case 7:  # Spiral Squares
            numberOfLoops = 8
            radiusSizeChange = 1

            pathX = [0]
            pathY = [0]

            for i in range(numberOfLoops):
                pathX.append(radiusSizeChange*(i+1))
                pathY.append(pathY[len(pathY)-1])

                pathX.append(radiusSizeChange*(i+1))
                pathY.append(radiusSizeChange*(i+1))

                pathX.append(-radiusSizeChange*(i+1))
                pathY.append(radiusSizeChange*(i+1))

                pathX.append(-radiusSizeChange*(i+1))
                pathY.append(-radiusSizeChange*(i+1))
        case 8: # modified lemniscate
            u = np.linspace(0, 30 * np.pi, 800)
            pathX = 1.4*(np.cos(u) + 0.05*u*np.sin(3*u))
            pathY = 1.4*(np.sin(2*u) + 0.05*u*np.cos(3*u))

        case default: #rectangle
            pathX = [ 5,  5,  5, 5, 5, 5, 3, 1, -1, -3, -5 , -5 , -5, -5, -5 , -5, -3, -1, 1, 3, 5]
            pathY = [-5, -3, -1, 1, 3, 5, 5, 5 , 5,  5,  5,   3,   1, -1, -3,  -5, -5, -5,-5,-5,-5]

    startupPlot(L1, L2)

# set up serial comms---------------------------------------------------------------------------------------------------
ser = serial.Serial('com4', 9600, timeout=10) # create Serial Object, baud = 9600, read times out after 10s
time.sleep(3)  # delay 3 seconds to allow serial com to get established

# Build GUI------------------------------------------------------------------------------------------------------------
tkTop = tk.Tk()  # Create GUI Box
tkTop.geometry('1200x800')  # size of GUI
tkTop.title("2 DOF GUI")  # title in top left of window

# Title on top middle of screen
Title = tk.Label(text='Enter the desired coordinates of the 2 DOF arm', font=("Courier", 14, 'bold')).pack()

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

# set initial coords to zero
x_coord_entry.insert(0,0)
y_coord_entry.insert(0,0)

UpdateCoordsButton = tk.Button(EntryFrame,
                                   text="Update Coordinates",
                                   command=lambda: set_coordinates_state(float(x_coord_entry.get()),float(y_coord_entry.get())),
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
startupPlot(L1, L2)

# run loop watching for gui interactions
tk.mainloop()