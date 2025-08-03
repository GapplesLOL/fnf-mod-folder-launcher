import os
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import subprocess
import json

# Try to import the Pillow library, which is needed to handle .ico files.
# If it's not installed, we'll handle the images gracefully by not showing them.
try:
    from PIL import Image, ImageTk
    has_pillow = True
except ImportError:
    has_pillow = False
    print("Pillow library not found. Install it with 'pip install Pillow' to enable .ico file support.")

# --- File System Logic ---

def find_first_executable_and_icon_in_folder(folder_path, executable_extensions):
    """
    Finds the first executable file and a corresponding icon file
    within a given directory and its subdirectories.

    Args:
        folder_path (str): The root directory to search.
        executable_extensions (list): A list of file extensions to identify executables.

    Returns:
        tuple or None: A tuple containing (executable_path, icon_path) or None if no
                       executable is found. icon_path will be None if no suitable icon
                       is found.
    """
    executable_path = None
    icon_path = None
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check for the executable
            if any(file.lower().endswith(ext) for ext in executable_extensions):
                executable_path = file_path
                
                # Now, look for a specific icon in the same directory.
                # Prioritize 'icon.ico', then 'icon.png', then 'icon.gif'.
                icon_file_names = ["icon.ico", "icon.png", "icon.gif"]
                for icon_name in icon_file_names:
                    candidate_icon_path = os.path.join(root, icon_name)
                    if os.path.exists(candidate_icon_path):
                        icon_path = candidate_icon_path
                        break
                
                # If an executable is found, we can return immediately
                return (executable_path, icon_path)
    return None

def get_first_level_folders_with_executables(start_directory, executable_extensions):
    """
    Generates a dictionary mapping first-level folder names to the paths of
    the first executable and its icon found within each folder's hierarchy.

    Args:
        start_directory (str): The path to the directory to start searching from.
        executable_extensions (list): A list of file extensions to identify executables.

    Returns:
        dict: A dictionary with folder names as keys and a tuple (executable_path, icon_path) as values.
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
            result = find_first_executable_and_icon_in_folder(item_path, executable_extensions)
            if result:
                executable_map[item_name] = result

    return executable_map

# --- Cache Logic ---

def get_cache_file_path(filename):
    """
    Returns the full path to a cache file in the user's home directory.
    """
    return os.path.join(os.path.expanduser('~'), filename)

def save_last_directory(directory_path):
    """
    Saves the provided directory path to the cache file.
    """
    try:
        with open(get_cache_file_path('.executable_launcher_cache'), 'w') as f:
            f.write(directory_path)
    except Exception as e:
        print(f"Warning: Could not save directory to cache. Error: {e}")

def load_last_directory():
    """
    Loads the last-used directory path from the cache file.
    Returns the path if successful, otherwise returns None.
    """
    cache_path = get_cache_file_path('.executable_launcher_cache')
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                directory_path = f.read().strip()
                if os.path.isdir(directory_path):
                    return directory_path
        except Exception as e:
            print(f"Warning: Could not load directory from cache. Error: {e}")
    return None

# --- Theme Management ---

THEME_FILE = get_cache_file_path('themes.json')

def load_themes():
    """Loads themes from the themes.json file."""
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_themes(themes):
    """Saves themes to the themes.json file."""
    try:
        with open(THEME_FILE, 'w') as f:
            json.dump(themes, f, indent=4)
    except Exception as e:
        print(f"Warning: Could not save themes. Error: {e}")

def get_default_themes():
    """Returns the hardcoded default themes, including new gaming company themes."""
    return {
        'Steam': {
            'bg_dark': '#1b2838',
            'bg': '#3b526b',
            'fg': 'white',
            'hover': '#2a475e',
            'click': '#417a9b',
            'label_fg': 'white',
            'label_bg': '#1b2838'
        },
        'Dark': {
            'bg_dark': '#2c3e50',
            'bg': '#34495e',
            'fg': 'white',
            'hover': '#3b526b',
            'click': '#4a6078',
            'label_fg': 'white',
            'label_bg': '#2c3e50'
        },
        'Nintendo': {
            'bg_dark': '#E60012',
            'bg': '#FF0018',
            'fg': 'white',
            'hover': '#CC0010',
            'click': '#B3000E',
            'label_fg': 'white',
            'label_bg': '#E60012'
        },
        'PlayStation': {
            'bg_dark': '#003399',
            'bg': '#004C99',
            'fg': 'white',
            'hover': '#002B7A',
            'click': '#002566',
            'label_fg': 'white',
            'label_bg': '#003399'
        },
        'Xbox': {
            'bg_dark': '#107C10',
            'bg': '#28A745',
            'fg': 'white',
            'hover': '#0C6A0C',
            'click': '#0A550A',
            'label_fg': 'white',
            'label_bg': '#107C10'
        },
        'Ubisoft': {
            'bg_dark': '#000000',
            'bg': '#1E2C3D',
            'fg': '#0090FF',
            'hover': '#2A3C50',
            'click': '#3A4E65',
            'label_fg': '#0090FF',
            'label_bg': '#000000'
        },
        'Blizzard': {
            'bg_dark': '#0070D7',
            'bg': '#1783D6',
            'fg': 'white',
            'hover': '#005CBF',
            'click': '#0050A4',
            'label_fg': 'white',
            'label_bg': '#0070D7'
        }
    }

def get_all_themes():
    """Combines default and user-saved themes."""
    themes = get_default_themes()
    user_themes = load_themes()
    themes.update(user_themes)
    return themes

def save_last_theme(theme_name):
    """Saves the last used theme name to a cache file."""
    try:
        with open(get_cache_file_path('.executable_launcher_theme_cache'), 'w') as f:
            f.write(theme_name)
    except Exception as e:
        print(f"Warning: Could not save theme to cache. Error: {e}")

def load_last_theme():
    """Loads the last used theme name from cache."""
    cache_path = get_cache_file_path('.executable_launcher_theme_cache')
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                theme_name = f.read().strip()
                return theme_name
        except Exception as e:
            print(f"Warning: Could not load theme from cache. Error: {e}")
    return 'Steam' # Default to Steam if no cache or error

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

def build_gui_buttons(parent_frame, folder_executable_map, button_font, theme_colors):
    """
    Clears the parent_frame and builds new buttons from the provided map.
    """
    # Clear existing widgets in the button frame
    for widget in parent_frame.winfo_children():
        widget.destroy()
    
    # List to hold references to PhotoImage objects to prevent garbage collection
    images = []

    if not folder_executable_map:
        label = tk.Label(parent_frame, text="No executable-containing folders found.",
                         pady=10, bg=theme_colors['label_bg'], fg=theme_colors['label_fg'], font=button_font)
        label.pack(fill=tk.X)
    else:
        # Sort the folder names alphabetically before creating buttons
        sorted_folder_names = sorted(folder_executable_map.keys())
        
        for folder_name in sorted_folder_names:
            executable_path, icon_path = folder_executable_map[folder_name]
            
            # Check for and load the icon if it exists
            photo = None
            if icon_path:
                try:
                    if has_pillow:
                        # Use Pillow to handle all image types for consistent resizing
                        image = Image.open(icon_path)
                        image.thumbnail((32, 32), Image.Resampling.LANCZOS) # Resize icon for the button
                        photo = ImageTk.PhotoImage(image)
                    else:
                        # Fallback for PNG and GIF if Pillow is not installed
                        if icon_path.lower().endswith(('.png', '.gif')):
                            photo = tk.PhotoImage(file=icon_path)
                    
                    if photo:
                        images.append(photo) # Keep a reference to prevent garbage collection
                except tk.TclError:
                    # Handle cases where the image file is corrupted or not a valid format
                    photo = None
                except Exception as e:
                    print(f"Could not load icon from {icon_path}. Error: {e}")
                    photo = None

            # Create the button with or without an icon
            button_args = {
                "text": folder_name,
                "command": create_button_command(executable_path),
                "font": button_font,
                "bg": theme_colors['bg'],
                "fg": theme_colors['fg'],
                "relief": "flat",
                "borderwidth": 0,
                "pady": 10
            }
            if photo:
                # Add the image and configure the button to show both text and image
                button_args["image"] = photo
                button_args["compound"] = "left"
            
            button = tk.Button(parent_frame, **button_args)

            # Add custom hover and click effects to the buttons
            button.bind("<Enter>", lambda e, b=button: b.config(bg=theme_colors['hover']))
            button.bind("<Leave>", lambda e, b=button: b.config(bg=theme_colors['bg']))
            button.bind("<Button-1>", lambda e, b=button: b.config(bg=theme_colors['click']))
            button.bind("<ButtonRelease-1>", lambda e, b=button: b.config(bg=theme_colors['hover']))
            button.pack(fill=tk.X, pady=(0, 5))
            
    # Store the images list on the parent_frame to prevent garbage collection
    parent_frame.images = images


def create_theme_editor_window(root_window, update_callback):
    """Creates a new window for customizing and saving themes."""
    editor_window = tk.Toplevel(root_window)
    editor_window.title("Theme Editor")
    editor_window.geometry("350x400")
    editor_window.configure(bg='#1b2838')

    current_theme = get_all_themes()[load_last_theme()]
    
    # Use an inner frame for padding
    main_frame = tk.Frame(editor_window, bg='#1b2838', padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Theme Name:", bg='#1b2838', fg='white').pack(pady=(0, 5))
    theme_name_entry = tk.Entry(main_frame, width=30)
    theme_name_entry.insert(0, load_last_theme())
    theme_name_entry.pack(pady=(0, 10))

    color_vars = {
        'bg_dark': tk.StringVar(value=current_theme['bg_dark']),
        'bg': tk.StringVar(value=current_theme['bg']),
        'fg': tk.StringVar(value=current_theme['fg']),
        'hover': tk.StringVar(value=current_theme['hover']),
        'click': tk.StringVar(value=current_theme['click']),
        'label_bg': tk.StringVar(value=current_theme['label_bg']),
        'label_fg': tk.StringVar(value=current_theme['label_fg'])
    }
    
    def choose_color(color_key):
        color_code = colorchooser.askcolor(title=f"Choose color for {color_key}")
        if color_code:
            color_vars[color_key].set(color_code[1])
            color_labels[color_key].config(bg=color_code[1])

    color_labels = {}
    color_keys = ['Main Background', 'Button Background', 'Button Text', 'Hover Color', 'Click Color']
    theme_keys = ['bg_dark', 'bg', 'fg', 'hover', 'click']

    for i in range(len(color_keys)):
        frame = tk.Frame(main_frame, bg='#1b2838')
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=color_keys[i], bg='#1b2838', fg='white', width=15, anchor='w').pack(side=tk.LEFT)
        color_labels[theme_keys[i]] = tk.Label(frame, text='', bg=color_vars[theme_keys[i]].get(), width=5, relief='solid')
        color_labels[theme_keys[i]].pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Pick", command=lambda key=theme_keys[i]: choose_color(key)).pack(side=tk.RIGHT)

    def save_theme():
        new_theme_name = theme_name_entry.get()
        if not new_theme_name:
            messagebox.showerror("Error", "Theme name cannot be empty.")
            return

        new_theme = {key: var.get() for key, var in color_vars.items()}
        # Ensure label colors are consistent for simplicity
        new_theme['label_bg'] = new_theme['bg_dark']
        new_theme['label_fg'] = new_theme['fg']

        all_themes = get_all_themes()
        all_themes[new_theme_name] = new_theme
        save_themes(all_themes)
        save_last_theme(new_theme_name)
        update_callback(new_theme_name)
        editor_window.destroy()
        messagebox.showinfo("Success", f"Theme '{new_theme_name}' saved and applied!")

    def apply_selected_theme():
        themes = get_all_themes()
        theme_name = theme_listbox.get(tk.ACTIVE)
        if theme_name in themes:
            update_callback(theme_name)
            save_last_theme(theme_name)
            editor_window.destroy()

    def delete_selected_theme():
        themes = load_themes()
        theme_name = theme_listbox.get(tk.ACTIVE)
        if theme_name in themes and messagebox.askyesno("Delete Theme", f"Are you sure you want to delete '{theme_name}'?"):
            del themes[theme_name]
            save_themes(themes)
            theme_listbox.delete(tk.ACTIVE)

    button_frame = tk.Frame(main_frame, bg='#1b2838')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Save & Apply", command=save_theme).pack(side=tk.LEFT, padx=5)
    
    # Theme Selection Frame
    selection_frame = tk.Frame(editor_window, bg='#1b2838', padx=20, pady=10)
    selection_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(selection_frame, text="Saved Themes:", bg='#1b2838', fg='white').pack()
    theme_listbox = tk.Listbox(selection_frame, bg='#3b526b', fg='white', selectbackground='#41a9b', relief='flat', height=5)
    for theme_name in get_all_themes().keys():
        theme_listbox.insert(tk.END, theme_name)
    theme_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
    
    select_frame = tk.Frame(selection_frame, bg='#1b2838')
    select_frame.pack(fill=tk.X)
    tk.Button(select_frame, text="Apply", command=apply_selected_theme).pack(side=tk.LEFT, expand=True)
    tk.Button(select_frame, text="Delete", command=delete_selected_theme).pack(side=tk.RIGHT, expand=True)
    
def run_launcher():
    """
    Main function to initialize and run the GUI application.
    """
    # Define common executable extensions to strictly target .exe files
    common_extensions = ['.exe']

    root = tk.Tk()
    root.title("Friday Night Funkin' Launcher")
    root.geometry("500x500")
    
    # Default theme name
    current_theme_name = load_last_theme()
    current_theme = get_all_themes().get(current_theme_name, get_default_themes()['Steam'])
    root.configure(bg=current_theme['bg_dark'])
    
    # Define a function to be called when the window is closed
    def on_close():
        save_last_theme(current_theme_name)
        root.destroy()

    # Bind the on_close function to the window's close protocol
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Define a nicer font
    button_font = ("Helvetica", 12, "bold")

    # Frame for control buttons and status
    control_frame = tk.Frame(root, bg=current_theme['bg_dark'], pady=10)
    control_frame.pack(fill=tk.X)

    # Label to show the current directory
    current_dir_label = tk.Label(control_frame, text="No directory selected.", bg=current_theme['bg_dark'], fg="white", font=("Helvetica", 10))
    current_dir_label.pack(side=tk.LEFT, padx=(10, 0), expand=True)
    
    # Theme selection dropdown
    theme_names = sorted(list(get_all_themes().keys()))
    theme_var = tk.StringVar(root)
    theme_var.set(current_theme_name)
    
    theme_dropdown = tk.OptionMenu(control_frame, theme_var, *theme_names, command=lambda x: update_gui(theme_name=theme_var.get()))
    theme_dropdown.config(bg=current_theme['bg'], fg=current_theme['fg'], relief="flat")
    theme_dropdown.pack(side=tk.RIGHT, padx=5)

    # Button to open theme editor
    theme_button = tk.Button(control_frame, text="Edit Theme", command=lambda: create_theme_editor_window(root, update_gui), bg=current_theme['bg'], fg=current_theme['fg'], relief="flat", padx=10)
    theme_button.pack(side=tk.RIGHT, padx=5)

    # Button to browse for a new directory
    def browse_directory():
        new_dir = filedialog.askdirectory(initialdir=current_dir_label.cget("text") if os.path.isdir(current_dir_label.cget("text")) else os.path.expanduser('~'))
        if new_dir:
            update_gui(directory=new_dir)

    browse_button = tk.Button(control_frame, text="Browse", command=browse_directory, bg=current_theme['bg'], fg=current_theme['fg'], relief="flat", padx=10)
    browse_button.pack(side=tk.RIGHT, padx=5)

    # Button to refresh the current directory
    def refresh_directory():
        current_dir = current_dir_label.cget("text")
        if os.path.isdir(current_dir):
            update_gui(directory=current_dir)
        else:
            messagebox.showinfo("No Directory", "Please select a valid directory first.")

    refresh_button = tk.Button(control_frame, text="Refresh", command=refresh_directory, bg=current_theme['bg'], fg=current_theme['fg'], relief="flat", padx=10)
    refresh_button.pack(side=tk.RIGHT, padx=5)
    
    # Main frame for the canvas and scrollbar
    main_frame = tk.Frame(root, padx=10, pady=10, bg=current_theme['bg_dark'])
    main_frame.pack(fill=tk.BOTH, expand=1)

    canvas = tk.Canvas(main_frame, bg=current_theme['bg_dark'], highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    canvas.configure(yscrollcommand=scrollbar.set)
    
    button_frame = tk.Frame(canvas, bg=current_theme['bg_dark'])
    # Store the ID of the window item to be able to configure it later
    button_frame_id = canvas.create_window((0, 0), window=button_frame, anchor="nw")

    def on_canvas_configure(event):
        """
        Handles the canvas resizing, ensuring the inner frame's width
        matches the canvas and the scroll region is updated correctly.
        """
        # Update the width of the button_frame to match the canvas width
        canvas.itemconfigure(button_frame_id, width=event.width)
        # Update the scroll region to account for the new size
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind the configure event to our new function to fix the resizing issue
    canvas.bind('<Configure>', on_canvas_configure)
    
    def update_gui(theme_name=None, directory=None):
        """
        Updates the GUI with new buttons or a new theme.
        """
        nonlocal current_theme, current_theme_name
        
        # Update theme if a new theme name is provided
        if theme_name:
            current_theme_name = theme_name
            current_theme = get_all_themes().get(current_theme_name, get_default_themes()['Steam'])
            
            # Update root window and control frame colors
            root.configure(bg=current_theme['bg_dark'])
            control_frame.configure(bg=current_theme['bg_dark'])
            main_frame.configure(bg=current_theme['bg_dark'])
            canvas.configure(bg=current_theme['bg_dark'])
            button_frame.configure(bg=current_theme['bg_dark'])
            
            # Update control button colors
            theme_button.config(bg=current_theme['bg'], fg=current_theme['fg'])
            browse_button.config(bg=current_theme['bg'], fg=current_theme['fg'])
            refresh_button.config(bg=current_theme['bg'], fg=current_theme['fg'])
            current_dir_label.config(bg=current_theme['bg_dark'], fg=current_theme['fg'])
            theme_dropdown.config(bg=current_theme['bg'], fg=current_theme['fg'])
            
            # Update the dropdown menu to reflect the new theme list if a new theme was saved
            new_theme_names = sorted(list(get_all_themes().keys()))
            menu = theme_dropdown["menu"]
            menu.delete(0, "end")
            for name in new_theme_names:
                menu.add_command(label=name, command=tk._setit(theme_var, name, update_gui))
            theme_var.set(current_theme_name)


        start_directory = directory if directory else current_dir_label.cget("text")
        
        # Save the new directory to cache
        if start_directory and os.path.isdir(start_directory):
            save_last_directory(start_directory)
            current_dir_label.config(text=start_directory)
        
        # Get the new mapping and build buttons
        if start_directory and os.path.isdir(start_directory):
            folder_executable_map = get_first_level_folders_with_executables(start_directory, common_extensions)
            build_gui_buttons(button_frame, folder_executable_map, button_font, current_theme)
        else:
            build_gui_buttons(button_frame, {}, button_font, current_theme)


    # Initial directory setup
    cached_directory = load_last_directory()
    if cached_directory:
        update_gui(directory=cached_directory)
    else:
        root.deiconify()
        start_directory = filedialog.askdirectory(initialdir=os.path.expanduser('~'))
        if start_directory:
            update_gui(directory=start_directory)
        else:
            messagebox.showinfo("Cancelled", "Directory selection cancelled.")
            root.destroy()
            return
            
    root.mainloop()

if __name__ == "__main__":
    run_launcher()
