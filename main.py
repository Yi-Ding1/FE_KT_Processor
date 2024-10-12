"""
Where it all begins... This program generates the front-end UI
Author: Yi Ding
Version: 1.1
Log: Added comments for readability.
"""

import tkinter as tk
from tree_library.json_tree_modified import create_json_tree
from tree_library.tree_validation import validate_tree
from tree_library.node_link_validation import process_linkage
from tkinter import filedialog, messagebox


# Function to handle file selection
def open_file_dialog(entry_field):
    file_path = filedialog.askopenfilename(
        title="Select a file", 
        filetypes=[("CSV Files", "*.csv")]
    )
    if file_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, file_path)


def display_options():
    # Create a window for options
    option_window = tk.Toplevel(root)
    option_window.title("Choose File Type")
    
    option_window.geometry("400x200")
    selected_option = tk.StringVar()  # Variable to store the selected option

    # Function to handle button clicks and close the option window
    def select_option(option):
        selected_option.set(option)  # Set the selected option
        option_window.destroy()  # Close the option window

    # Create buttons for the two options
    btn_option1 = tk.Button(option_window, text="Serial Numbers", command=lambda: select_option("Option 1"),
                            bg="lightblue", fg="black", font=("Helvetica", 14, "bold"))
    btn_option2 = tk.Button(option_window, text="Written Strings", command=lambda: select_option("Option 2"),
                            bg="lightblue", fg="black", font=("Helvetica", 14, "bold"))

    btn_option1.pack(pady=20, padx=20, fill="both", expand=True)
    btn_option2.pack(pady=20, padx=20, fill="both", expand=True)

    # Wait for the user to select an option
    option_window.grab_set()  # Make the option window modal
    option_window.wait_window()  # Wait until the window is closed

    return selected_option.get()  # Return the selected option


# Function to process files based on user input
def process_files():

    if validate_linkage_var.get():
        selected_option = display_options()
        if not selected_option:
            messagebox.showwarning("No Files Processed", "No process method selected for linkages.")
            return

    # ask for output directory
    output_directory = filedialog.askdirectory(
    title="Select the directory to save the output files"
    )
    file_paths = {}

    # collect file paths to various key files
    if tree_data_path.get():
        file_paths['tree_data'] = tree_data_path.get()
    if study_design_path.get():
        file_paths['study_design'] = study_design_path.get()
    if keys_data_path.get():
        file_paths['key_data'] = keys_data_path.get()
    if link_data_path.get():
        file_paths['link_data'] = link_data_path.get()

    # process the files based on selected options
    try:
        method_selected = False
        if create_json_var.get():
            method_selected = True
            create_json_tree(file_paths['tree_data'], output_directory)
        if validate_tree_var.get():
            method_selected = True
            output_file_txt = f"{output_directory}/knowledge_tree_report.txt"
            validate_tree(file_paths['key_data'], file_paths['study_design'], file_paths['tree_data'], output_file_txt)
        if validate_linkage_var.get() and selected_option:
            method_selected = True
            process_linkage(selected_option, file_paths['tree_data'], file_paths['link_data'], output_directory)
            
    except Exception as e:
        messagebox.showwarning("An Error Occurred", f"Error: {e}")
        return

    # successful execution, yeah!
    if method_selected:
        messagebox.showinfo("Success", f"Files saved to {output_directory}")
    else:
        messagebox.showwarning("No Files Processed", "No process method selected.")

# Create the main window
root = tk.Tk()  # Use TkinterDnD's main window for drag and drop
root.title("Knowledge Tree Processing Application")
root.config(bg='#f0f8ff')  # Light color background (AliceBlue)

# Set a uniform padding for better layout
PADX, PADY = 20, 10

# Create fields to hold file paths
tree_data_path = tk.Entry(root, width=40)
study_design_path = tk.Entry(root, width=40)
keys_data_path = tk.Entry(root, width=40)
link_data_path = tk.Entry(root, width=40)

# Checkboxes to select processing methods
create_json_var = tk.BooleanVar()
validate_tree_var = tk.BooleanVar()
validate_linkage_var = tk.BooleanVar()

create_json_checkbox = tk.Checkbutton(root, text="Create Json Tree", variable=create_json_var, bg='#f0f8ff')
validate_tree_checkbox = tk.Checkbutton(root, text="Validate Json Tree", variable=validate_tree_var, bg='#f0f8ff')
validate_linkage_checkbox = tk.Checkbutton(root, text="Validate Linkage", variable=validate_linkage_var, bg='#f0f8ff')

# Buttons to open file dialogs
open_tree_data_button = tk.Button(root, text="Open File 1", command=lambda: open_file_dialog(tree_data_path), bg='#add8e6')
open_study_design_button = tk.Button(root, text="Open File 2", command=lambda: open_file_dialog(study_design_path), bg='#add8e6')
open_keys_data_button = tk.Button(root, text="Open File 3", command=lambda: open_file_dialog(keys_data_path), bg='#add8e6')
open_link_data_button = tk.Button(root, text="Open File 4", command=lambda: open_file_dialog(link_data_path), bg='#add8e6')

# Button to process files
process_button = tk.Button(root, text="Process and Save Files", command=process_files, bg='#4682b4', fg='white')

# Layout for the UI with better padding
tk.Label(root, text="Select File 1 For Knowledge Tree:", bg='#f0f8ff').grid(row=0, column=0, padx=PADX, pady=PADY, sticky="e")
tree_data_path.grid(row=0, column=1, padx=PADX, pady=PADY)
create_json_checkbox.grid(row=4, column=0, padx=PADX, pady=PADY)
open_tree_data_button.grid(row=0, column=3, padx=PADX, pady=PADY)

tk.Label(root, text="Select File 2 For Current Study Design:", bg='#f0f8ff').grid(row=1, column=0, padx=PADX, pady=PADY, sticky="e")
study_design_path.grid(row=1, column=1, padx=PADX, pady=PADY)
validate_tree_checkbox.grid(row=4, column=1, padx=PADX, pady=PADY)
open_study_design_button.grid(row=1, column=3, padx=PADX, pady=PADY)

tk.Label(root, text="Select File 3 For Chosen Topics:", bg='#f0f8ff').grid(row=2, column=0, padx=PADX, pady=PADY, sticky="e")
keys_data_path.grid(row=2, column=1, padx=PADX, pady=PADY)
validate_linkage_checkbox.grid(row=4, column=2, padx=PADX, pady=PADY)
open_keys_data_button.grid(row=2, column=3, padx=PADX, pady=PADY)

tk.Label(root, text="Select File 4 For Node Linkages:", bg='#f0f8ff').grid(row=3, column=0, padx=PADX, pady=PADY, sticky="e")
link_data_path.grid(row=3, column=1, padx=PADX, pady=PADY)
open_link_data_button.grid(row=3, column=3, padx=PADX, pady=PADY)

process_button.grid(row=5, columnspan=4, pady=PADY)
tk.Label(root, text="Version: 2.0", bg='#f0f8ff').grid(row=5, column=3, padx=PADX, pady=PADY, sticky="e")

# Start the main event loop
root.mainloop()
