# 8/15/2024
# Sherry Choi
# added CSV file import and export

import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import numpy as np
import sys
import os
import time
import pandas as pd
from tkinter import filedialog

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from xarm.wrapper import XArmAPI
from scipy.spatial.transform import Rotation as R

# Initialize the robot arm
arm = XArmAPI('192.168.1.200')
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(0)

global T1, T2, marker
# global variables
trajectory_points = {}
marker = np.array([])
T1 = np.array([])
T2 = np.array([])

def import_marker_points(file_path):
    global marker
    df = pd.read_csv(file_path)
    if df.empty:
        messagebox.showinfo("Empty File", "The selected file has no data.")
    else:
        marker = df.values
    return df


def load_marker_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = import_marker_points(file_path)
        if not df.empty:
            print("Marker Points: \n", df)
            update_status("Please import trajectory points.")
        else:
            messagebox.showinfo("Load Issue", "No data was loaded. Please check the file format and contents.")
    else:
        messagebox.showinfo("File Load Cancelled", "No file was selected.")
def import_trajectory_points(file_path):
    global T1, T2
    df = pd.read_csv(file_path, delimiter=',')
    trajectory_points = df.to_numpy()
    if len(trajectory_points) >= 1:
        T1 = trajectory_points[0, :]
    if len(trajectory_points) >= 2:
        T2 = trajectory_points[1, :]
    return trajectory_points

def load_trajectory_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        trajectory_points = import_trajectory_points(file_path)
        if trajectory_points is not None:
            print('Trajectory Points: \n', trajectory_points)
            manual_mode_button['state'] = 'normal'
            remote_mode_button['state'] = 'normal'
            record_safepoint_button['state'] = 'normal'
            update_status("Please move to a safe point in remote mode and record it.")
            arm.set_mode(5)
            arm.set_state(0)
            window.bind("<KeyPress>", remote_mode)
        else:
            messagebox.showinfo("Empty File", "The selected file has no data")
    else:
        messagebox.showinfo("File Load Cancelled", "No file was selected.")

Probot = []
Probot_display = []


def manual_mode(): # manual mode - to move the arm manually
    arm.set_mode(2)  # Mode for manual control
    arm.set_state(0)
    update_status("In Manual Mode. \n You could move the arm manually.")

def activate_remote_mode(): # remote mode - use keyboard to control movements
    arm.set_mode(5)
    arm.set_state(0)
    update_status("In Remote Mode. \n Use keyboard to move the arm.")
    window.bind("<KeyPress>", remote_mode)

def remote_mode(event):
    velocity = 20  # Velocity per second
    duration = 0.05  # Duration to move in each touch

    if event.keysym == 'Left':
        arm.vc_set_cartesian_velocity([0, -velocity, 0, 0, 0, 0])
        time.sleep(duration)
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])  # Stop movement
    elif event.keysym == 'Right':
        arm.vc_set_cartesian_velocity([0, velocity, 0, 0, 0, 0])
        time.sleep(duration)
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])  # Stop movement
    elif event.keysym == 'Up':
        arm.vc_set_cartesian_velocity([-velocity, 0, 0, 0, 0, 0])
        time.sleep(duration)
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])  # Stop movement
    elif event.keysym == 'Down':
        arm.vc_set_cartesian_velocity([velocity, 0, 0, 0, 0, 0])
        time.sleep(duration)
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])  # Stop movement
    elif event.keysym == 'W' or event.keysym == 'w':
        arm.vc_set_cartesian_velocity([0, 0, velocity, 0, 0, 0])
        time.sleep(duration)
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])  # Stop movement
    elif event.keysym == 'S' or event.keysym == 's':
        arm.vc_set_cartesian_velocity([0, 0, -velocity, 0, 0, 0])
        time.sleep(duration)
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])  # Stop movement


def display_key_instructions(): # keyboard instructions to 
    instruction_window = tk.Toplevel()
    instruction_window.title("Remote Mode Keyboard Instructions")
    instructions = f"Key Assignments for Movements: \n- Move Right(-x): → \n- Move Left(x): ← \n- Move Forward(y): ↑ \n- Move Backward(-y): ↓ \n- Move Up(z): W \n- Move Down(-z): S"
    label = tk.Label(instruction_window, text=instructions, font=button_font, justify=tk.LEFT)
    label.pack(padx=10, pady=10)


def record_safepoint():
    status, position = arm.get_position(is_radian=False)
    global safepoint_robot
    safepoint_robot = position
    update_status(f"Safe Point Recorded. \n Move the arm to trajectory point 1 in REMOTE MODE.")

    arm.set_mode(5)
    arm.set_state(0)
    window.bind("<KeyPress>", remote_mode)

    record_button['state'] = 'normal'
    undo_button['state'] = 'normal'
    complete_button['state'] = 'normal'
    T1_button['state'] = 'disabled'
    T2_button['state'] = 'disabled'
    safepoint_button['state'] = 'disabled'
    record_safepoint_button['state'] = 'disabled'


def record_position():
    global Probot, Probot_display
    try:
        status, position = arm.get_position(is_radian=False)
        Probot.append(position)
        formatted_position = sigfig(position)
        Probot_display.append(formatted_position)
        update_points_list()

        current_point = len(Probot)
        total_points = len(marker)

        if current_point < total_points:
            update_status(f"Point {current_point} saved, move to Point {current_point + 1} to register.")
        else:
            update_status(
                f"Point {total_points} registered, please move the arm to a safe area. \n Then press CALCULATE to get trajectory positions.")
            record_button['state'] = 'disabled'
    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete():
    try:
        selection = points_list.curselection()[0]
        del Probot[selection]
        del Probot_display[selection]
        update_points_list()
    except IndexError:
        messagebox.showerror("Error", "No position selected to delete.")


def undo():
    global Probot, Probot_display
    if Probot:
        removed_point = len(Probot)
        Probot.pop()
        Probot_display.pop()
        update_points_list()
        update_status(f"Point {removed_point} removed, register Point {removed_point} again.")
        record_button['state'] = 'normal'


# /////calculation//////
def rotation(marker, Probot):
    Probot_array = np.array(Probot)
    Cmri = np.mean(marker[:, :3], axis=0)
    Crobot = np.mean(Probot_array[:, :3], axis=0)
    marker2 = marker[:, :3] - Cmri
    Probot2 = Probot_array[:, :3] - Crobot
    H = np.dot(Probot2.T, marker2)
    U, S, Vt = np.linalg.svd(H)
    Rm = np.dot(U, Vt)
    if np.linalg.det(Rm) < 0:
        Vt[-1, :] *= -1
        Rm = np.dot(U, Vt)
    d = Crobot - np.dot(Rm, Cmri)
    return R.from_matrix(Rm), d


def transformation(trajectory_points, Rm, d):
    transformed_points = []
    for point in trajectory_points:
        positions = point[:3]
        orientations = point[3:]
        transformed_positions = Rm.apply(positions) + d
        quaternions = R.from_euler('xyz', orientations, degrees=True)
        rotated_quaternions = Rm * quaternions
        transformed_euler_angles = rotated_quaternions.as_euler('xyz', degrees=True)
        transformed_point = np.hstack([transformed_positions, transformed_euler_angles])
        transformed_points.append(transformed_point)
    return np.array(transformed_points)


# showing 3 sig fig values only
def sigfig(value):
    if isinstance(value, (float, int)):
        return f"{value:.3g}"
    elif isinstance(value, np.ndarray):
        vectorized_format = np.vectorize(lambda x: f"{x:.3g}")
        if value.ndim == 1:
            return ", ".join(vectorized_format(value))
        else:
            return "\n".join(", ".join(row) for row in vectorized_format(value))
    elif isinstance(value, (list, np.ndarray)):
        formatted_values = [f"{x:.3g}" for x in value]
        return f"[{', '.join(formatted_values)}]"
    else:
        raise ValueError("Unsupported type. Only floats, ints, and numpy arrays are supported")


def transform_T1_T2(Rm, d):
    global T1_robot, T2_robot, safepoint_robot
    T1_robot = transformation(np.array([T1]), Rm, d)[0]
    T2_robot = transformation(np.array([T2]), Rm, d)[0]
    Rm_matrix = Rm.as_matrix()
    formatted_T1 = sigfig(T1_robot)
    formatted_T2 = sigfig(T2_robot)
    formatted_Rm = sigfig(Rm_matrix)
    formatted_d = sigfig(d)
    mean_tre, std_tre, tre_values = registration_error(marker, Probot, Rm, d)
    formatted_mean = sigfig(mean_tre)
    formatted_sd = sigfig(std_tre)
    display_position = tk.Label(Reference_window,
                                text=str(
                                    f"T1: [{formatted_T1}]\n\n T2: [{formatted_T2}]\n\n Rotation Matrix R: \n[{formatted_Rm}]\n\n Translation Vector d: [{formatted_d}] \n\n Registration Error: [{formatted_sd}mm]"),
                                font=("Helvetica", 12))
    display_position.pack(pady=5)
    print(Probot)
    print("T1: ", T1_robot)
    print("T2: ", T2_robot)
    print("R: ", Rm_matrix)
    print("d: ", d)
    print("mean tre: ", mean_tre)
    print("sd of tre: ", std_tre)
    print("tre value:", tre_values)


def complete_recording():
    Rm, d = rotation(marker, Probot)
    transform_T1_T2(Rm, d)
    arm.set_mode(0)
    arm.set_state(0)
    record_button['state'] = 'disabled'
    undo_button['state'] = 'normal'
    safepoint_button['state'] = 'normal'
    T1_button['state'] = 'normal'
    T2_button['state'] = 'normal'
    manual_mode_button['state'] = 'normal'
    remote_mode_button['state'] = 'normal'
    update_status(f"Positions T1 T2 calculated.")


def move_T1():
    arm.set_mode(5)
    arm.set_state(0)
    arm.vc_set_cartesian_velocity([0, 0, 30, 0, 0, 0])
    time.sleep(1.5)
    arm.set_mode(0)
    arm.set_state(0)
    x, y, z, roll, pitch, yaw = safepoint_robot
    arm.set_position(x, y, z, roll, pitch, yaw, speed=50, wait=True)
    update_status("Moving to Safepoint")
    x, y, z, roll, pitch, yaw = T1_robot
    arm.set_position(x, y, z + 40, roll, pitch, yaw, speed=50, wait=True)
    time.sleep(1)
    arm.set_position(x, y, z, roll, pitch, yaw, speed=20, wait=True)
    update_status(f"Moving to T1")


def move_T2():
    arm.set_mode(5)
    arm.set_state(0)
    arm.vc_set_cartesian_velocity([0, 0, 30, 0, 0, 0])
    time.sleep(1.5)
    arm.set_mode(0)
    arm.set_state(0)
    x, y, z, roll, pitch, yaw = safepoint_robot
    arm.set_position(x, y, z, roll, pitch, yaw, speed=50, wait=True)
    update_status("Moving to Safepoint")
    x, y, z, roll, pitch, yaw = T2_robot
    arm.set_position(x, y, z + 40, roll, pitch, yaw, speed=50, wait=True)
    time.sleep(1)
    arm.set_position(x, y, z, roll, pitch, yaw, speed=20, wait=True)
    update_status(f"Moving to T2")


def goto_safepoint():
    arm.set_mode(5)
    arm.set_state(0)
    arm.vc_set_cartesian_velocity([0, 0, 30, 0, 0, 0])
    time.sleep(1.5)
    arm.set_mode(0)
    arm.set_state(0)
    x, y, z, roll, pitch, yaw = safepoint_robot
    arm.set_position(x, y, z, roll, pitch, yaw, speed=50, wait=True)
    update_status("Moving to Safepoint")


def stop():
    arm.emergency_stop()


def update_points_list():
    points_list.delete(0, tk.END)
    for i, point in enumerate(Probot_display):
        points_list.insert(tk.END, f"Point {i + 1}: {point}")


def update_status(message):
    status_label.config(text=message, font=('Helvetica', 13))


def registration_error(marker, Probot, Rm, d):
    marker = np.array(marker)
    Probot = np.array(Probot)
    transformed_positions = Rm.apply(marker[:, :3] + d)
    tre_values = np.linalg.norm(transformed_positions - Probot[:, :3], axis=1)
    mean_tre = np.mean(tre_values)
    std_tre = np.std(tre_values)

    return mean_tre, std_tre, tre_values

def save_file():
    global T1_robot, T2_robot
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        point = {
            'Point': ['T1', 'T2'],
            'x': [T1_robot[0], T2_robot[0]],
            'y': [T1_robot[1], T2_robot[1]],
            'z': [T1_robot[2], T2_robot[2]],
            'roll': [T1_robot[3], T2_robot[3]],
            'pitch': [T1_robot[4], T2_robot[4]],
            'yaw': [T1_robot[5], T2_robot[5]],
        }
        df = pd.DataFrame(point)
        df.to_csv(file_path, index=False)
        messagebox.showinfo("File Saved", f"Transformed points saved to {file_path}")
    else:
        messagebox.showinfo("File Save Cancelled", "No file was saved.")

# GUI setup
window = tk.Tk()
window.title("xArm Control Interface")
window.geometry("520x400")

button_font = ('Helvetica', 13)
display_key_instructions()
Reference_window = tk.Toplevel(window, height=100, width=400)
Reference_window.title("Reference")

menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Import Marker Points", command=load_marker_file)
file_menu.add_command(label="Import Trajectory Points", command=load_trajectory_file)
file_menu.add_command(label="Export Transformed Trajectory Points", command=save_file)
menu_bar.add_cascade(label="File", menu=file_menu)
window.config(menu=menu_bar)



record_safepoint_button = tk.Button(window, text="Record SafePoint", state='disabled', command=record_safepoint,
                                    font=button_font)
record_safepoint_button.grid(row=0, column=0, padx=5, pady=5)

manual_mode_button = tk.Button(window, text="MANUAL MODE", state='disabled', command=manual_mode, font=button_font)
manual_mode_button.grid(row=0, column=1, sticky='e', padx=5, pady=5)

remote_mode_button = tk.Button(window, text="REMOTE MODE", state='disabled', command=activate_remote_mode, font=button_font)
remote_mode_button.grid(row=0, column=2, padx=5, pady=5)

stop_button = tk.Button(window, text="STOP", bg="red", fg="white", command=stop, font=button_font)
stop_button.grid(row=0, column=3, sticky='e', padx=5, pady=5)

record_button = tk.Button(window, text="RECORD", state='disabled', command=record_position, font=button_font)
record_button.grid(row=2, column=0, padx=5, pady=5)

undo_button = tk.Button(window, text="UNDO", state='disabled', command=undo, font=button_font)
undo_button.grid(row=2, column=1, padx=5, pady=5)

# delete_button = tk.Button(window, text="DELETE", state='disabled', command=delete)
# delete_button.grid(row=2, column=2, sticky='w', padx=5, pady=5)

complete_button = tk.Button(window, text="CALCULATE", state='disabled', command=complete_recording, font=button_font)
complete_button.grid(row=2, column=2, padx=5, pady=5)

points_list = tk.Listbox(window, width=80, font=button_font)
points_list.grid(row=1, column=0, columnspan=3, sticky='we', padx=5, pady=5)

T1_button = tk.Button(window, text="Move to T1", state='disabled', command=move_T1, font=button_font)
T1_button.grid(row=3, column=0, padx=5, pady=5)

safepoint_button = tk.Button(window, text="Move to Safepoint", state='disabled', command=goto_safepoint,
                             font=button_font)
safepoint_button.grid(row=3, column=1, padx=5, pady=5)

T2_button = tk.Button(window, text="Move to T2", state='disabled', command=move_T2, font=button_font)
T2_button.grid(row=3, column=2, padx=5, pady=5)

status_label = tk.Label(window, text="Please import Marker Points.", bg='green', fg='white', font=button_font)
status_label.grid(row=4, column=0, columnspan=3, sticky='ew', padx=5, pady=5)



window.columnconfigure(1, weight=1)
window.mainloop()


