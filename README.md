# xArm Registration GUI

A Python-based GUI for fiducial marker registration and trajectory transformation using the **xArm robotic arm**. This project is designed for **preclinical neurosurgical applications**, drawing inspiration from the **ROSA robotic system**.

The interface allows researchers to:
- Import marker and trajectory data
- Control the arm in both manual and remote modes
- Perform real-time spatial registration using SVD
- Export transformed trajectory points for robotic tool guidance

## Features

- Manual and keyboard-based remote control of xArm
- Import/export marker and trajectory data (CSV format)
- SVD-based registration: compute rotation matrix and translation vector
- Transformation of trajectory points in 3D space
- Registration error calculation and visualization
- Emergency stop and safe zone handling
- Intuitive GUI built with Tkinter

## Project Background

**xArm** is a robotic surgical arm designed for use in neurosurgery, inspired by the **ROSA robotic arm**. This project is under active development to support enhanced surgical registration and targeting processes in translational research.


## Setup Procedure:
1. Download UFACTORY Studio
   https://www.ufactory.cc/ufactory-studio/
2. Connect the wire from silver box to your device
3. Turn on the xArm (red button on the side of the box) and wait for 2 beeps
4. XArm IP Setup.pdf
https://uthtmc.sharepoint.com/:b:/r/sites/TranslationalBiomimeticBioelectronicsLab2/Shared%20Documents/General/TBBL%20Weekly%20Updates/Summer%20Researchers/Jay%20Natarajan/XArm%20IP%20Setup.pdf?csf=1&web=1&e=v9Tq4X
5. XArm Robot Guidewire Insertion Procedure.pdf  https://uthtmc.sharepoint.com/:b:/r/sites/TranslationalBiomimeticBioelectronicsLab2/Shared%20Documents/General/TBBL%20Weekly%20Updates/Summer%20Researchers/Jay%20Natarajan/XArm%20Robot%20Guidewire%20Insertion%20Procedure.pdf?csf=1&web=1&e=eQYwDj

## Python Code Connection:
1. Connect wire from silver box to computer
2. Connect xArm on UFACTORY Studio
3. Download and open the file 'xArm_Registration_GUI.py'
4. Install all python modules listed in the file
   - VSCode reference: (https://uthtmc.sharepoint.com/:w:/r/sites/TranslationalBiomimeticBioelectronicsLab2/Shared%20Documents/General/TBBL%20Weekly%20Updates/Summer%20Researchers/Sherry%20Choi/xArm%20in%20VS%20Code%20.docx?d=wdfc95e30ddfd445cafa9d042edc27780&csf=1&web=1&e=lptLzC)

## Registration Process:
1. Make sure the arm could reach to all fiducial/marker points vertically
2. Run the code
3. [**Import Marker Points**] in CSV file in the "File" menu
4. [**Import Trajectory Points**] in CSV file the "File" menu
   - Marker Points and Trajectory Points files could be found in Model/Sheep Testing Data folder
5. Move the arm to a safe point in remote mode and record it with [**Record SafePoint**]
   -  Manual Mode: Move the arm manually
   -  Remote Mode: Use keyboard to control the arm. A Remote Mode Keyboard Instruction is provided
6. Move the arm to desired fiducial position in Remote Mode
7. Press [**RECORD**] to record the position once registered
8. If you want to remove the previous recorded position, press [**UNDO**]
9. Repeat steps 5-7 to record all marker positions
10. Move the arm to the SafePoint area registered to avoid collision later when moving
11. Press [**CALCULATE**] to calculate the rotation matrix R, translation vector d, and trajectory points T1 T2
12. Press [**Move to Safepoint**] before going to any trajectory point to avoid collision
13. Press [**Move to T1**] to direct the arm to T1
14. Press [**Move to T2**] to direct the arm to T2
15. [**Export Transformed Trajectory Points**] in CSV file in the "File" menu

## Reset the Arm:
- Go to UFACTORY Studio, continue pressing "ZERO POSITION"
- If you want to go back to remote mode, click "REMOTE MODE" on GUI to proceed
  
## Emergency Stop (stopping the xarm):
- GUI 'STOP' button on the top right corner
- UFACTORY Studio 'STOP' button on the top right corner
- Physical RED BUTTON on the silver box next to the robot

## End the prgram:
- Close the Main GUI window

## Error:
- If error occured, go to UFACTORY Studio. Read the pop up Error message and Click "Clear error". 
- To avoid self-collision, make sure to keep joint 5 and 6 to the front.
