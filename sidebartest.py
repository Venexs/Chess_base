from tkinter import Tk, Canvas, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH

root = Tk()
root.geometry("200x600")
root.resizable(False, False)

# 1. Create a vertical Scrollbar
scrollbar = Scrollbar(root, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)

# 2. Create the Canvas and link its scrolling to the scrollbar
canvas = Canvas(
    root,
    bg="#FFFFFF",
    height=600,
    width=180,  # Leaves 20px room for the scrollbar within the 200px window
    bd=0,
    highlightthickness=0,
    relief="ridge",
    yscrollcommand=scrollbar.set  # Tells canvas to update the scrollbar position
)
canvas.pack(side=LEFT, fill=BOTH, expand=True)

# Configure the scrollbar to control the canvas vertical view
scrollbar.config(command=canvas.yview)

# Tracking variables for text placement
line_counter = 1
current_y = 10  # Starting Y coordinate for the first line of text
line_spacing = 25  # Space between each line

def add_log_line():
    global current_y, line_counter
    
    # Create the text line on the canvas (anchor="w" aligns text to the left)
    canvas.create_text(
        15, 
        current_y, 
        text=f"Line {line_counter}: Event logged.", 
        anchor="w", 
        fill="#333333"
    )
    
    # Increment tracking variables for the NEXT line
    current_y += line_spacing
    line_counter += 1
    
    # IMPORTANT: Update the canvas scrollable area to encompass all text items
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    # AUTO-SCROLL: Snap the view to the absolute bottom (1.0 = 100% down)
    canvas.yview_moveto(1.0)
    
    # Loop back into this function exactly 1 second (1000 milliseconds) later
    root.after(1000, add_log_line)

# Start the repeating text loop
add_log_line()

root.mainloop()