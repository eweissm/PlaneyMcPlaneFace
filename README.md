# Autonomous-Zen-Garden
Shown below is an automatic Zen Garden, which uses a 2 DOF SCARA robot arm to position a ball bearing moving through the sand. This project consisted of numerous elements, including:
  -	The design of a continuous rotation SCARA arm and its integration into the wooden housing
    -This involved a vibration analysis to prevent the stepper motor from exciting an unlucky natural frequency of the box, causing an obnoxious noise.
  - A hall effect homing sensor
  -	Wiring the microcontrollers and various servos or stepper motors
  -	Coding for the Arduino
    -	This involved a homing sequence which would occur on system power up.
    -	Additionally, this involved two-way serial communication with the controlling computer.
      -	The Arduino would receive the desired joint angles from the Python, estimate the time for the move, send this estimation to the python, complete the joint moves (both joints arriving at the same time), and finally communicate to the python that the moves were complete, and the next joint angles could be sent.
  -	Coding the controller in Python
    -	Used a root finding algorithm to find the optimal path and joint angles for the robotic arm. 
    -	A custom GUI was developed, which would take user input and use serial communication to talk with an Arduino to control the joint angles. Shown below is the UI, which outlines the workspace of the robot (black dotted line) and the selected preset path the arm can follow when the “follow path” button is pressed (blue dotted line). The user can scroll through various presets by selecting the “Change Path” button. Finally, if the user inputs custom X and Y coordinates, once the “Update Coordinates” button is pressed, the arm will move to that location, and the arm joint angles and position will be shown. 
    -	The preset paths can be passed through a parametric equation or through a G-code file via a custom regex interpreter I wrote for basic G-code commands.

## Images:
![Untitled video - Made with Clipchamp](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/3ab6f555-8f9d-4b08-80e6-b3ee96074b49)
![IMG_0028](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/15c103ee-035d-467a-a6fa-9733e9d6d9fe)
![IMG_0029](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/b6828620-6f0a-4bb1-a02a-6950a32e25bc)
![image](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/f3c0ebd9-a533-49c8-9401-8787ef99986c)
![image](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/b1ae802a-1f63-4505-8897-12f492a7b84f)
![image](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/28735282-b4a3-40a8-ac62-01b68e120c47)
![image](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/4fe4bf65-0a0a-4657-aa0f-83cb1f476d7b)
![image](https://github.com/eweissm/Autonomous-Zen-Garden/assets/73143081/12a7cdce-9d46-4a08-bb95-5e2cd24955fa)
