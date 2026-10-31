import tkinter as tk
from tkinter import Canvas, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH

# ==============================================================================
# 1. MAIN WINDOW SETUP (e.g., your Chess Board Window)
# ==============================================================================
root = tk.Tk()
root.geometry("600x600")
root.title("Chess Game")

# Quick placeholder label just to show it's the main window
main_label = tk.Label(root, text="MAIN CHESS WINDOW (600x600)", font=("Arial", 14))
main_label.pack(expand=True)


# ==============================================================================
# 2. SIDE LOG WINDOW SETUP (200x600)
# ==============================================================================
# Toplevel makes this a separate window that belongs to the main root window
side_win = tk.Toplevel(root)
side_win.title("Logs")
side_win.geometry("200x600")
side_win.resizable(False, False)

# Prevents the side window from having its own taskbar icon; 
# also forces it to minimize/maximize/close together with the main window.
side_win.transient(root) 

# Re-creating the scrollable canvas inside side_win
scrollbar = Scrollbar(side_win, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)

canvas = Canvas(
    side_win,
    bg="#FFFFFF",
    height=600,
    width=180,
    bd=0,
    highlightthickness=0,
    relief="ridge",
    yscrollcommand=scrollbar.set
)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=canvas.yview)


# ==============================================================================
# 3. STICKY WINDOW WINDOW TRACKING LOGIC
# ==============================================================================
def sync_windows(event=None):
    # Ensure we only recalculate when the MAIN window moves, not its child widgets
    if event and event.widget != root:
        return
    
    # 1. Get current position and size of the main window
    main_x = root.winfo_x()
    main_y = root.winfo_y()
    main_w = root.winfo_width()
    main_h = root.winfo_height()
    
    # 2. Define side window fixed dimensions
    side_w = 200
    side_h = 600
    
    # 3. Calculate position coordinates:
    # Left edge of side window = Right edge of main window
    new_x = main_x + main_w
    
    # Vertical middle of side window = Vertical middle of main window
    new_y = main_y + int(main_h / 2) - int(side_h / 2)
    
    # 4. Snap the side window to the calculated coordinates
    side_win.geometry(f"{side_w}x{side_h}+{new_x}+{new_y}")

# Bind the main window's movement/scaling to our sync function
root.bind("<Configure>", sync_windows)


# ==============================================================================
# 4. LOG GENERATOR LOOP (From previous turn)
# ==============================================================================
line_counter = 1
current_y = 20
line_spacing = 25

def add_log_line():
    global current_y, line_counter
    canvas.create_text(
        15, 
        current_y, 
        text=f"Line {line_counter}: Event logged.", 
        anchor="w", 
        fill="#333333"
    )
    current_y += line_spacing
    line_counter += 1
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1.0)
    root.after(1000, add_log_line)

# Start logging loop
add_log_line()

# Trigger an initial snap right after initialization clears
root.after(10, sync_windows)

root.mainloop()