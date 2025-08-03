import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import subprocess

# --- File System Logic ---

def find_first_executable_in_folder(folder_path, executable_extensions):
    """
    Finds the first executable file within a given directory and its subdirectories.

    Args:
        folder_path (str): The root directory to search.
        executable_extensions (list): A list of file extensions to identify executables.

    Returns:
        str or None: The full path to the first executable found, or None if none are found.
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Check ONLY by .exe file extension as requested.
            if any(file.lower().endswith(ext) for ext in executable_extensions):
                return file_path
    return None

def get_first_level_folders_with_executables(start_directory, executable_extensions):
    """
    Generates a dictionary mapping first-level folder names to the paths of
    the first executable found within each folder's hierarchy.

    Args:
        start_directory (str): The path to the directory to start searching from.
        executable_extensions (list): A list of file extensions to identify executables.

    Returns:
        dict: A dictionary with folder names as keys and executable paths as values.
    """
    executable_map = {}
    if not os.path.isdir(start_directory):
        messagebox.showerror("Error", f"The directory '{start_directory}' does not exist.")
        return executable_map

    # Get the first-level subdirectories
    first_level_items = os.listdir(start_directory)
    for item_name in first_level_items:
        item_path = os.path.join(start_directory, item_name)
        if os.path.isdir(item_path):
            # Find an executable within this subdirectory's tree
            executable_path = find_first_executable_in_folder(item_path, executable_extensions)
            if executable_path:
                # Add the mapping if an executable was found
                executable_map[item_name] = executable_path

    return executable_map

# --- Cache Logic ---

def get_cache_file_path():
    """
    Returns the full path to the cache file in the user's home directory.
    """
    return os.path.join(os.path.expanduser('~'), '.executable_launcher_cache')

def save_last_directory(directory_path):
    """
    Saves the provided directory path to the cache file.
    """
    try:
        with open(get_cache_file_path(), 'w') as f:
            f.write(directory_path)
    except Exception as e:
        print(f"Warning: Could not save directory to cache. Error: {e}")

def load_last_directory():
    """
    Loads the last-used directory path from the cache file.
    Returns the path if successful, otherwise returns None.
    """
    cache_path = get_cache_file_path()
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                directory_path = f.read().strip()
                if os.path.isdir(directory_path):
                    return directory_path
        except Exception as e:
            print(f"Warning: Could not load directory from cache. Error: {e}")
    return None

# --- GUI Logic ---

def create_button_command(executable_path):
    """
    Creates a command function to be executed when a button is pressed.
    This function launches the specified executable without blocking the GUI.
    """
    def launch_executable():
        try:
            # Get the directory of the executable
            executable_dir = os.path.dirname(executable_path)
            
            # Using subprocess.Popen to launch the process non-blocking.
            # We use the 'cwd' (current working directory) parameter to set the working
            # directory for the new process to be the same as the executable's folder.
            subprocess.Popen(executable_path, cwd=executable_dir, shell=True)
            # messagebox.showinfo("Success", f"Launched: {os.path.basename(executable_path)}") # This line is for testing purposes only. It should be commented out for the final result.
        except FileNotFoundError:
            messagebox.showerror("Error", f"Executable not found at: {executable_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    return launch_executable

def build_gui_buttons(parent_frame, folder_executable_map, button_font, button_colors):
    """
    Clears the parent_frame and builds new buttons from the provided map.
    """
    # Clear existing widgets in the button frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    if not folder_executable_map:
        label = tk.Label(parent_frame, text="No executable-containing folders found.",
                         pady=10, bg=button_colors['bg_dark'], fg="white", font=button_font)
        label.pack(fill=tk.X)
    else:
        # Sort the folder names alphabetically before creating buttons
        sorted_folder_names = sorted(folder_executable_map.keys())
        
        for folder_name in sorted_folder_names:
            executable_path = folder_executable_map[folder_name]
            button = tk.Button(
                parent_frame,
                text=folder_name,
                command=create_button_command(executable_path),
                font=button_font,
                bg=button_colors['bg'],
                fg=button_colors['fg'],
                relief="flat",
                borderwidth=0,
                pady=10
            )
            # Add custom hover and click effects to the buttons
            button.bind("<Enter>", lambda e, b=button: b.config(bg=button_colors['hover']))
            button.bind("<Leave>", lambda e, b=button: b.config(bg=button_colors['bg']))
            button.bind("<Button-1>", lambda e, b=button: b.config(bg=button_colors['click']))
            button.bind("<ButtonRelease-1>", lambda e, b=button: b.config(bg=button_colors['hover']))
            button.pack(fill=tk.X, pady=(0, 5))

def run_launcher():
    """
    Main function to initialize and run the GUI application.
    """
    # Define common executable extensions to strictly target .exe files
    common_extensions = ['.exe']

    root = tk.Tk()
    root.title("Friday Night Funkin' Launcher")
    root.geometry("500x500")
    
    # Configure the main window for a dark steam theme
    main_bg = "#1b2838"
    root.configure(bg=main_bg)

    # Define a nicer font and color scheme
    button_font = ("Helvetica", 12, "bold")
    button_colors = {
        'bg_dark': main_bg,
        'bg': "#3b526b",
        'fg': "white",
        'hover': "#2a475e",
        'click': "#417a9b"
    }

    # Frame for control buttons and status
    control_frame = tk.Frame(root, bg=main_bg, pady=10)
    control_frame.pack(fill=tk.X)

    # Label to show the current directory
    current_dir_label = tk.Label(control_frame, text="No directory selected.", bg=main_bg, fg="white", font=("Helvetica", 10))
    current_dir_label.pack(side=tk.LEFT, padx=(10, 0), expand=True)

    # Button to browse for a new directory
    def browse_directory():
        new_dir = filedialog.askdirectory(initialdir=current_dir_label.cget("text") if os.path.isdir(current_dir_label.cget("text")) else os.path.expanduser('~'))
        if new_dir:
            update_gui(new_dir)

    browse_button = tk.Button(control_frame, text="Browse", command=browse_directory, bg=button_colors['bg'], fg=button_colors['fg'], relief="flat", padx=10)
    browse_button.pack(side=tk.RIGHT, padx=(0, 5))

    # Button to refresh the current directory
    def refresh_directory():
        current_dir = current_dir_label.cget("text")
        if os.path.isdir(current_dir):
            update_gui(current_dir)
        else:
            messagebox.showinfo("No Directory", "Please select a valid directory first.")

    refresh_button = tk.Button(control_frame, text="Refresh", command=refresh_directory, bg=button_colors['bg'], fg=button_colors['fg'], relief="flat", padx=10)
    refresh_button.pack(side=tk.RIGHT)
    
    # Main frame for the canvas and scrollbar
    main_frame = tk.Frame(root, padx=10, pady=10, bg=main_bg)
    main_frame.pack(fill=tk.BOTH, expand=1)

    canvas = tk.Canvas(main_frame, bg=main_bg, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    button_frame = tk.Frame(canvas, bg=main_bg)
    canvas.create_window((0, 0), window=button_frame, anchor="nw")
    
    def update_gui(start_directory):
        """
        Updates the GUI with buttons for a new directory.
        """
        # Save the new directory to cache
        save_last_directory(start_directory)
        
        # Update the directory label
        current_dir_label.config(text=start_directory)
        
        # Get the new mapping and build buttons
        folder_executable_map = get_first_level_folders_with_executables(start_directory, common_extensions)
        build_gui_buttons(button_frame, folder_executable_map, button_font, button_colors)

    # Initial directory setup
    cached_directory = load_last_directory()
    if cached_directory:
        update_gui(cached_directory)
    else:
        root.deiconify()
        start_directory = filedialog.askdirectory(initialdir=os.path.expanduser('~'))
        if start_directory:
            update_gui(start_directory)
        else:
            messagebox.showinfo("Cancelled", "Directory selection cancelled.")
            root.destroy()
            return
            
    root.mainloop()

if __name__ == "__main__":
    run_launcher()
