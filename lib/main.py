import tkinter as tk
from tkinter import ttk
import os
import sys
import json
import io
import contextlib
import importlib.util
from datetime import datetime

# Dynamically import leagueScheduler, validateSchedule, and utils from the local lib folder
lib_path = os.path.join(os.path.dirname(__file__), 'lib') if not __file__.endswith('lib\main.py') else os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

def import_from_lib(module_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(lib_path, f"{module_name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

leagueScheduler = import_from_lib('leagueScheduler')
validator = import_from_lib('validateSchedule')
utils = import_from_lib('utils')

schedule = None  # Declare at the top

# Create the main application window
root = tk.Tk()
root.title("League Scheduler Client")
root.geometry("600x400")

# Output label (use a Text widget for multi-line output)
output_label = ttk.Label(root, text="Schedule Output:")
output_label.pack(pady=(20, 0))

output_box = tk.Text(root, height=15, width=70)
output_box.pack(pady=10)

def set_output_text(text):
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, text)

def save_schedule_to_file(schedule_str, filename_prefix="schedule_output"):
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_time_%H-%M-%S")
    filename = f"{filename_prefix}_{date_str}.txt"
    file_path = os.path.join(results_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(schedule_str)

def save_validation_results_to_file(results_str, filename_prefix="validation_results"):
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(results_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_time_%H-%M-%S")
    filename = f"{filename_prefix}_{date_str}.txt"
    file_path = os.path.join(results_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(results_str)

def on_generate_schedule():
    global schedule
    schedule = leagueScheduler.build_schedule(utils.load_configs())
    schedule_str = leagueScheduler.format_schedule(schedule)
    save_schedule_to_file(schedule_str)  # Save to file before displaying
    set_output_text(schedule_str)

def on_validate_schedule():
    global schedule
    # Capture the output of the validation functions
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        validation_results = validator.build_validation_results(schedule=schedule, config=utils.load_configs())

    output = buf.getvalue()
    results_str = validator.format_validation_results(validation_results) + "\n\n" + leagueScheduler.format_schedule(schedule)
    set_output_text(results_str)
    save_validation_results_to_file(results_str)  # Save validation results to file

# Generate Schedule button
generate_btn = ttk.Button(root, text="Generate Schedule", command=on_generate_schedule)
generate_btn.pack(pady=5)

# Validate Schedule button
validate_btn = ttk.Button(root, text="Validate Schedule", command=on_validate_schedule)
validate_btn.pack(pady=5)

def copy_selection():
    try:
        # Try to get selected text
        selected = output_box.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        # If nothing is selected, copy all text
        selected = output_box.get("1.0", "end-1c")
    root.clipboard_clear()
    root.clipboard_append(selected)

# Create the context menu
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Copy", command=copy_selection)

def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

# Bind right-click to show the context menu
output_box.bind("<Button-3>", show_context_menu)

# Start the GUI event loop
root.mainloop()