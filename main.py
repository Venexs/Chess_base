from tkinter import Tk, Canvas, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH, Toplevel
from PIL import Image, ImageTk
import json

root = Tk()
root.geometry("600x600")

canvas = Canvas(
    root,
    bg = "#FFFFFF",
    height = 600,
    width = 600,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)
canvas.place(x = 0, y = 0)

canvas.create_rectangle(295,295,305,305, fill="#000000", outline="") # Center point
                        #Coordinates of the rectangle (top left set, bottom right set)

# ? Global points ======================
global clicked_on_piece
global piece_loc
global positions
global possible_pos
global piece_tag
global clr
global grid_clr
global en_passant_target
global turn

grid_clr={}
possible_pos=[]
enemy_pos=[]
positions=[]
piece_loc=""
clicked_on_piece=""
piece_tag=""
clr=""
en_passant_target=""
turn=0 # 0 = White, 1 = Black
piece_size=(50,50)

position_pawn_list_white=["A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2"]
position_pawn_list_black=["A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7"]

# ? ==============================================================================
# ? SIDE LOG WINDOW SETUP (200x600)
# ? ==============================================================================

# Toplevel makes this a separate window that belongs to the main root window
side_win = Toplevel(root)
side_win.title("Logs")
side_win.geometry("200x600")
side_win.resizable(False, False)

# Prevents the side window from having its own taskbar icon; 
# also forces it to minimize/maximize/close together with the main window.
side_win.transient(root) 

# Re-creating the scrollable canvas inside side_win
scrollbar = Scrollbar(side_win, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)

canvas2 = Canvas(
    side_win,
    bg="#FFFFFF",
    height=600,
    width=180,
    bd=0,
    highlightthickness=0,
    relief="ridge",
    yscrollcommand=scrollbar.set
)
canvas2.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=canvas2.yview)

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

# ? ==============================================================================
# ? LOGS setup
# ? ==============================================================================

line_counter = 1
current_y = 20
line_spacing = 25

def add_log_line(piece, prev, next, capture=False, cap_piece="none"):
    global current_y, line_counter
    enemy_clr = "black" if clr == "white" else "white"
    if capture==False:
        canvas2.create_text(
            15, 
            current_y, 
            text=f"{clr} {piece}: {prev} -> {next}", 
            anchor="w", 
            fill="#333333"
        )

    else:
        canvas2.create_text(
            15, 
            current_y, 
            text=f"{clr} {piece}: {prev} -> {next} ║", 
            anchor="w", 
            fill="#333333"
        )
        canvas2.create_text(
            15, 
            current_y+15, 
            text=f"Taking {enemy_clr} {cap_piece}", 
            anchor="w", 
            fill="#333333"
        )
        current_y+=15
    current_y += line_spacing
    line_counter += 1
    canvas2.configure(scrollregion=canvas2.bbox("all"))
    canvas2.yview_moveto(1.0)

# ? ==========================================================================================
# ? ==========================================================================================
# ? ==========================================================================================

def invert_turn():
    global turn
    if turn==0: turn=1
    else: turn=0

def on_square_click(event,op_place=False,n_place="A1",takes=False):
    global clicked_on_piece
    global en_passant_target
    global possible_pos
    global enemy_pos

    tags = canvas.gettags("current")

    # ignore clicks that are not squares
    if "square" not in tags:
        return
    
    print(tags)

    if takes==True:
        square = tags[3]  # now guaranteed to be like "A1"
        print("Clicked square:", square)

    else:
        if op_place==False:
            square = tags[0]  # now guaranteed to be like "A1"
            print("Clicked square:", square)
        else:
            square = tags[-1]  # now guaranteed to be like "A1"
            print("Clicked square:", square)

    if clicked_on_piece and (square in possible_pos):
        old_square=canvas.gettags(clicked_on_piece)[3]
        name_of_piece=canvas.gettags(clicked_on_piece)[0]
        invert_turn()
        pawn_str=False

        new_coordinates = coordinate_tag_loc[square]
        new_x = (new_coordinates[0] + new_coordinates[2]) / 2
        new_y = (new_coordinates[1] + new_coordinates[3]) / 2

        canvas.coords(clicked_on_piece, new_x, new_y)
        canvas.tag_raise(clicked_on_piece)

        final_piece_list=set(canvas.find_withtag(clr)) & set(canvas.find_withtag(piece_tag)) & set(canvas.find_withtag(piece_loc))
        if final_piece_list:
            final_piece=final_piece_list.pop()
            piece_tags_list = list(canvas.gettags(final_piece))

            # SAFE PAWN CHECK: Look for strings directly in the current piece tags
            # SAFE PAWN CHECK
            if "pawn" in piece_tags_list:
                pawn_str = True
                if "True" in piece_tags_list: piece_tags_list.remove("True")
                if True in piece_tags_list: piece_tags_list.remove(True)
                if "False" in piece_tags_list: piece_tags_list.remove("False")

            if piece_loc in piece_tags_list:
                piece_tags_list.remove(piece_loc)
            
            # This will land safely at index 3
            piece_tags_list.append(square) 

            if pawn_str:
                # Append "False" after the square so tag order stays
                piece_tags_list.append("False")

                # --- NEW: EN PASSANT TARGET LOGIC ---
                old_row = int(piece_loc[1])  # e.g., '2' from "A2"
                new_row = int(square[1])     # e.g., '4' from "A4"
                
                # Check if the pawn moved exactly 2 squares vertically
                if abs(new_row - old_row) == 2:
                    # Calculate the row it skipped over
                    skipped_row = str((old_row + new_row) // 2)
                    en_passant_target = square[0] + skipped_row
                else:
                    en_passant_target = "" # Reset if it was a normal pawn step
            else:
                en_passant_target = "" # Reset if a non-pawn piece moved

            canvas.itemconfig(final_piece, tags=tuple(piece_tags_list))

        new_square=canvas.gettags(final_piece)[3]

        add_log_line(name_of_piece, old_square, new_square)

        default_squares()
        possible_pos=[]
        enemy_pos=[]

        clicked_on_piece = ""

        print(new_x, new_y) 

def calculate_moves(tags, piece_loc, clr, friendly_pos, enemy_pos):
    """Calculates all possible squares a piece can move to or attack."""
    valid_moves = []
    
    col_start = piece_loc[1]
    row_start = piece_loc[0]
    col_start_p = piece_loc[0]
    row_start_p = piece_loc[1]

    if "rook" in tags:
        col_idx = rows_tags.index(col_start_p)
        row_idx = colm_tags.index(row_start_p)
        ROOK_DELTAS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in ROOK_DELTAS:
            blocked = False
            for k in range(1, 8):
                if not blocked:
                    r = row_idx + dr * k
                    c = col_idx + dc * k
                    if not (0 <= r <= 7 and 0 <= c <= 7):
                        break
                    square = rows_tags[c] + colm_tags[r]
                    if square in friendly_pos:
                        blocked = True
                        break
                    if square in enemy_pos:
                        valid_moves.append(square)
                        blocked = True
                        break
                    valid_moves.append(square)

    elif "knight" in tags:
        col_idx = colm_tags.index(col_start)
        row_idx = rows_tags.index(row_start)
        KNIGHT_DELTAS = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        for dr, dc in KNIGHT_DELTAS:
            r = row_idx + dr
            c = col_idx + dc
            if 0 <= r <= 7 and 0 <= c <= 7:
                square = rows_tags[r] + colm_tags[c]
                if square not in friendly_pos:
                    valid_moves.append(square)

    elif "bishop" in tags:
        col_idx = colm_tags.index(col_start)
        row_idx = rows_tags.index(row_start)
        BISHOP_DELTAS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in BISHOP_DELTAS:
            for k in range(1, 8):
                r = row_idx + dr * k
                c = col_idx + dc * k
                if not (0 <= r <= 7 and 0 <= c <= 7):
                    break
                square = rows_tags[r] + colm_tags[c]
                if square in friendly_pos:
                    break
                if square in enemy_pos:
                    valid_moves.append(square)
                    break
                valid_moves.append(square)

    elif "queen" in tags:
        # Horizontal & Vertical sweeps
        for s in positions:
            if not s.startswith(row_start): continue
            valid_moves.append(s)
            if s in enemy_pos: break
        for s in positions:
            if not s.endswith(col_start): continue
            valid_moves.append(s)
            if s in enemy_pos: break

        # Diagonal sweeps
        col_idx = colm_tags.index(col_start)
        row_idx = rows_tags.index(row_start)
        BISHOP_DELTAS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in BISHOP_DELTAS:
            for k in range(1, 8):
                r = row_idx + dr * k
                c = col_idx + dc * k
                if not (0 <= r <= 7 and 0 <= c <= 7):
                    break
                square = rows_tags[r] + colm_tags[c]
                if square in friendly_pos:
                    break
                if square in enemy_pos:
                    valid_moves.append(square)
                    break
                valid_moves.append(square)

    elif "king" in tags:
        col_idx = colm_tags.index(col_start)
        row_idx = rows_tags.index(row_start)
        KING_DELTAS = [
            (-1, 0), (1, 0), (0, -1), (0, 1),   
            (1, 1), (1, -1), (-1, 1), (-1, -1)  
        ]
        for dr, dc in KING_DELTAS:
            r = row_idx + dr
            c = col_idx + dc
            if 0 <= r <= 7 and 0 <= c <= 7:
                square = rows_tags[r] + colm_tags[c]
                if square not in friendly_pos:
                    valid_moves.append(square)

    elif "pawn" in tags:
        pawn_col = piece_loc[0]
        pawn_row = piece_loc[1]
        col_idx = rows_tags.index(pawn_col)
        row_idx = colm_tags.index(pawn_row)
        direction = -1 if clr == "white" else 1
        has_not_moved = "True" in tags or True in tags

        r_1 = row_idx + direction
        if 0 <= r_1 <= 7:
            square_1 = rows_tags[col_idx] + colm_tags[r_1]
            if square_1 not in friendly_pos and square_1 not in enemy_pos:
                valid_moves.append(square_1)
                if has_not_moved:
                    r_2 = row_idx + (2 * direction)
                    if 0 <= r_2 <= 7:
                        square_2 = rows_tags[col_idx] + colm_tags[r_2]
                        if square_2 not in friendly_pos and square_2 not in enemy_pos:
                            valid_moves.append(square_2)

        for dc in [-1, 1]:
            r_diag = row_idx + direction
            c_diag = col_idx + dc
            if 0 <= r_diag <= 7 and 0 <= c_diag <= 7:
                diag_square = rows_tags[c_diag] + colm_tags[r_diag]
                if diag_square in enemy_pos:
                    valid_moves.append(diag_square)

    return valid_moves

def highlight_piece(event):
    global clicked_on_piece, piece_loc, possible_pos, piece_tag, clr

    default_squares()
    item = canvas.find_withtag("current")[0]
    tags = canvas.gettags(item)
    piece_tag = tags[0]
    clr = tags[1]

    clicked_on_piece = item
    piece_loc = get_item_pos(item)

    # Dynamically fetch coordinates using our robust helper function
    enemy_clr = "black" if clr == "white" else "white"
    enemy_items = set(canvas.find_withtag(enemy_clr)) & set(canvas.find_withtag("piece"))
    enemy_pos = [get_item_pos(i) for i in enemy_items if get_item_pos(i)]

    friendly_items = set(canvas.find_withtag(clr)) & set(canvas.find_withtag("piece"))
    friendly_pos = [get_item_pos(i) for i in friendly_items if get_item_pos(i)]

    # Calculate raw theoretical moves
    raw_moves = calculate_moves(tags, piece_loc, clr, friendly_pos, enemy_pos)

    # --- SIMULATE MOVES TO REMOVE SELF-CHECKING SQUARES ---
    legal_moves = []
    for move_sq in raw_moves:
        orig_tags = list(canvas.gettags(clicked_on_piece))
        
        # Temporarily replace old position tag with simulated destination tag
        simulated_tags = [move_sq if t == piece_loc else t for t in orig_tags]
        canvas.itemconfig(clicked_on_piece, tags=tuple(simulated_tags))
        
        # If this hypothetical move does not leave our King in check, it is legal
        if not is_in_check(clr):
            legal_moves.append(move_sq)
            
        # Revert changes instantly before the frame updates
        canvas.itemconfig(clicked_on_piece, tags=tuple(orig_tags))

    possible_pos = legal_moves
    
    # Extra cleanup filtering for friendly obstructions
    blocked_squares = set()
    for sq in possible_pos:
        items = (
            set(canvas.find_withtag(sq)) &
            set(canvas.find_withtag(clr)) &
            set(canvas.find_withtag("piece"))
        )
        if items:
            blocked_squares.add(sq)

    possible_pos = [sq for sq in possible_pos if sq not in blocked_squares]
    
    print("Legal options:", possible_pos)
    show_squares()    

def show_squares():
    for sq in possible_pos:
        square_items = (
            set(canvas.find_withtag(sq)) &
            set(canvas.find_withtag("square"))
        )

        for item in square_items:
            canvas.itemconfig(item, fill="#82FFAA")

def default_squares():
    for sq in possible_pos:
        square_items = (
            set(canvas.find_withtag(sq)) &
            set(canvas.find_withtag("square"))
        )

        for item in square_items:
            canvas.itemconfig(item, fill=grid_clr[sq])

def mainframe_bar(event,op_place=False,n_place="A1",takes=True):
    global possible_pos, turn, clicked_on_piece, enemy_pos, clr, piece_tag, piece_loc, en_passant_target
    
    # 1. Grab the specific item on the canvas that was clicked
    item = canvas.find_withtag("current")[0]
    tags = canvas.gettags(item)
    
    # 2. Extract which square coordinate this piece is sitting on
    clicked_piece_square = None
    for t in tags:
        if t in positions:
            clicked_piece_square = t
            break
            
    # 3. If a friendly piece is active, and this piece sits on a green valid square, execute capture!
    if clicked_on_piece and clicked_piece_square and (clicked_piece_square in possible_pos):
        # Delete captured enemy piece from board
        old_square=canvas.gettags(clicked_on_piece)[3]
        name_of_piece=canvas.gettags(clicked_on_piece)[0]

        captured_piece=canvas.gettags(item)[0]

        canvas.delete(item)
        
        invert_turn()
        pawn_str = False

        # Move the friendly piece into position
        new_coordinates = coordinate_tag_loc[clicked_piece_square]
        new_x = (new_coordinates[0] + new_coordinates[2]) / 2
        new_y = (new_coordinates[1] + new_coordinates[3]) / 2

        canvas.coords(clicked_on_piece, new_x, new_y)
        canvas.tag_raise(clicked_on_piece)

        # Update the moving friendly piece's location tags
        final_piece_list = set(canvas.find_withtag(clr)) & set(canvas.find_withtag(piece_tag)) & set(canvas.find_withtag(piece_loc))
        if final_piece_list:
            final_piece = final_piece_list.pop()
            piece_tags_list = list(canvas.gettags(final_piece))

            if "pawn" in piece_tags_list:
                pawn_str = True
                if "True" in piece_tags_list: piece_tags_list.remove("True")
                if True in piece_tags_list: piece_tags_list.remove(True)
                if "False" in piece_tags_list: piece_tags_list.remove("False")

            if piece_loc in piece_tags_list:
                piece_tags_list.remove(piece_loc)
            
            piece_tags_list.append(clicked_piece_square)

            if pawn_str:
                piece_tags_list.append("False")
            
            en_passant_target = "" # Captures reset en passant availability

            canvas.itemconfig(final_piece, tags=tuple(piece_tags_list))

        new_square=canvas.gettags(final_piece)[3]

        add_log_line(name_of_piece, old_square, new_square, True, captured_piece)

        # Clear board state
        default_squares()
        possible_pos = []
        enemy_pos = []
        clicked_on_piece = ""
        print(new_x, new_y)
    else:
        # Otherwise, the player is choosing/highlighting a piece to move
        highlight_piece(event)

def get_center_from_key(key):
    json_path="positions_val.json"
    with open(json_path, "r") as f:
        data = json.load(f)

    if key not in data:
        raise KeyError(f"{key} not found in JSON")

    x1, y1, x2, y2 = data[key]
    avg_x = (x1 + x2) / 2
    avg_y = (y1 + y2) / 2

    return avg_x, avg_y

def piece_pos(piece):
    place=canvas.gettags(piece)[3]
    pos_x, posy = get_center_from_key(place)
    canvas.coords(piece, pos_x, posy)

def image_resize(image_path):
    image_bfr = Image.open(image_path)
    resized_img = image_bfr.resize(piece_size, Image.LANCZOS)

    return ImageTk.PhotoImage(resized_img)

def is_in_check(color):
    """Returns True if the specified color's King is under attack."""
    # 1. Locate the King
    king_items = set(canvas.find_withtag(color)) & set(canvas.find_withtag("king"))
    if not king_items:
        return False
    king_item = list(king_items)[0]
    king_pos = get_item_pos(king_item)

    enemy_clr = "black" if color == "white" else "white"
    
    # 2. Map current positions of all active pieces safely
    all_enemy_items = set(canvas.find_withtag(enemy_clr)) & set(canvas.find_withtag("piece"))
    all_friendly_items = set(canvas.find_withtag(color)) & set(canvas.find_withtag("piece"))
    
    enemy_positions = [get_item_pos(i) for i in all_enemy_items if get_item_pos(i)]
    friendly_positions = [get_item_pos(i) for i in all_friendly_items if get_item_pos(i)]

    # 3. Check if any enemy piece can hit the King's square
    for item in all_enemy_items:
        tags = canvas.gettags(item)
        piece_loc_local = get_item_pos(item)
        if not piece_loc_local:
            continue
        
        enemy_moves = calculate_moves(tags, piece_loc_local, enemy_clr, enemy_positions, friendly_positions)
        if king_pos in enemy_moves:
            return True

    return False

def get_item_pos(item):
    """Safely extracts the current square position tag from a piece."""
    tags = canvas.gettags(item)
    for t in tags:
        if t in positions:
            return t
    return ""

# ? ==========================================================================================
# ? ===================================== Board Creation =====================================
# ? ==========================================================================================

canvas.create_line(50,50,50,550,width=3) # Left line
canvas.create_line(550,50,550,550,width=3) # Right line
canvas.create_line(50,550,550,550,width=3) # Bottom line
canvas.create_line(50,50,550,50,width=3) # Top line

# The vertical Gap lines
gap_length=new_gap=62.5
for k in range(7):
    canvas.create_line(50+new_gap,50,50+new_gap,550,width=2)
    new_gap+=gap_length

# The Horizontal Gap lines
gap_length=new_gap=62.5
for k in range(7):
    canvas.create_line(50,50+new_gap,550,50+new_gap,width=2)
    new_gap+=gap_length


# The Zig-Zag chess pattern
square_gap_len=62.5
new_len=0
verical_gap=62.5
v_new_gap=0

rows_tags=["A", "B", "C", "D", "E", "F", "G", "H"]
colm_tags=["8", "7", "6", "5", "4", "3", "2", "1"]

coordinate_tag_loc={}

col_count=0
row_count=0
induvi=0

fix_piece="A1"

for row in range(8):
    for col in range(8):
        x1 = 50 + col * square_gap_len
        y1 = 50 + row * verical_gap
        x2 = x1 + square_gap_len
        y2 = y1 + verical_gap

        tag_str = rows_tags[col] + colm_tags[row]

        color = "#F5F5F5" if (row + col) % 2 == 0 else "#4F4F4F"

        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            tags=(tag_str, "square")
        )

        canvas.tag_bind(tag_str, "<Button-1>", on_square_click)

        coordinate_tag_loc[tag_str] = [x1, y1, x2, y2]
        grid_clr[tag_str] = color
        positions.append(tag_str)

        
        # --- square label ---
        #cx = (x1 + x2) / 2
        #cy = (y1 + y2) / 2

        #canvas.create_text(
        #    cx, cy,
        #    text=tag_str,
        #    fill="#777777",
        #    font=("Arial", 8),
        #    tags=("square_label",)
        #)
        
        row_count+=1
    col_count+=1
    row_count=0


# ? ==========================================================================================
# ? ================================== Initializer of images =================================
# ? ==========================================================================================
# Rook:
canvas.rook_image = image_resize("assets/rook.png")
# Knight:
canvas.knight_image = image_resize("assets/knight.png")
# Bishop:
canvas.bishop_image = image_resize("assets/bishop.png")
# Queen:
canvas.queen_image = image_resize("assets/queen.png")
# King:
canvas.king_image = image_resize("assets/king.png")
# Pawn:
canvas.pawn_image = image_resize("assets/pawn.png")

# ! ==============================

# Rook:
canvas.b_rook_image = image_resize("assets/other_rook.png")
# Knight:
canvas.b_knight_image = image_resize("assets/other_knight.png")
# Bishop:
canvas.b_bishop_image = image_resize("assets/other_bishop.png")
# Queen:
canvas.b_queen_image = image_resize("assets/other_queen.png")
# King:
canvas.b_king_image = image_resize("assets/other_king.png")
# Pawn:
canvas.b_pawn_image = image_resize("assets/other_pawn.png")

# ! Rook Piece Test
w_rook=canvas.create_image(
    0, 0,
    image=canvas.rook_image,
    tag=("rook","white","piece","A1"))

canvas.tag_bind(w_rook, "<Button-1>", mainframe_bar)
piece_pos(w_rook)

# ! Knight Piece Test
w_knight=canvas.create_image(
    0, 0,
    image=canvas.knight_image,
    tag=("knight","white","piece","B1"))

canvas.tag_bind(w_knight, "<Button-1>", mainframe_bar)
piece_pos(w_knight)

# ! Bishop Piece Test
w_bishop=canvas.create_image(
    0, 0,
    image=canvas.bishop_image,
    tag=("bishop","white","piece","C1"))

canvas.tag_bind(w_bishop, "<Button-1>", mainframe_bar)
piece_pos(w_bishop)

# ! Rook Piece Test 2
w_rook_2=canvas.create_image(
    0, 0,
    image=canvas.rook_image,
    tag=("rook","white","piece","H1"))

canvas.tag_bind(w_rook_2, "<Button-1>", mainframe_bar)
piece_pos(w_rook_2)

# ! Knight Piece Test 2
w_knight_2=canvas.create_image(
    0,0,
    image=canvas.knight_image,
    tag=("knight","white","piece","G1"))

canvas.tag_bind(w_knight_2, "<Button-1>", mainframe_bar)
piece_pos(w_knight_2)

# ! Bishop Piece Test 2
w_bishop_2=canvas.create_image(
    0,0,
    image=canvas.bishop_image,
    tag=("bishop","white","piece","F1"))

canvas.tag_bind(w_bishop_2, "<Button-1>", mainframe_bar)
piece_pos(w_bishop_2)

# ! Queen Piece Test
w_queen=canvas.create_image(
    0,0,
    image=canvas.queen_image,
    tag=("queen","white","piece","E1"))

canvas.tag_bind(w_queen, "<Button-1>", mainframe_bar)
piece_pos(w_queen)

# ! King Piece Test
w_king=canvas.create_image(
    0,0,
    image=canvas.king_image,
    tag=("king","white","piece","D1"))

canvas.tag_bind(w_king, "<Button-1>", mainframe_bar)
piece_pos(w_king)

# ! ==========================================================================================
# ! Pawn WHITE
# ! ==========================================================================================

pawn_list_white=[]
for k in range(8):
    pawn_list_white.append(
        canvas.create_image(
            0, 0,
            image=canvas.pawn_image,
            tag=("pawn","white","piece",position_pawn_list_white[k],"True"))
    )
    canvas.tag_bind(pawn_list_white[k], "<Button-1>", mainframe_bar)
    piece_pos(pawn_list_white[k])

#========================================================================================================
#========================================================================================================
#========================================================================================================

# ! Black King Test
b_king=canvas.create_image(
    0, 0,
    image=canvas.b_king_image,
    tag=("king","black","piece","E8"))

canvas.tag_bind(b_king, "<Button-1>", mainframe_bar)
piece_pos(b_king)

# ! Queen Black Test
b_queen=canvas.create_image(
    0,0,
    image=canvas.b_queen_image,
    tag=("queen","black","piece","D8"))

canvas.tag_bind(b_queen, "<Button-1>", mainframe_bar)
piece_pos(b_queen)

# ! Bishop Black Test
b_bishop=canvas.create_image(
    0,0,
    image=canvas.b_bishop_image,
    tag=("bishop","black","piece","C8"))

canvas.tag_bind(b_bishop, "<Button-1>", mainframe_bar)
piece_pos(b_bishop)

# ! Bishop Black Test
b_bishop=canvas.create_image(
    0,0,
    image=canvas.b_bishop_image,
    tag=("bishop","black","piece","C8"))

canvas.tag_bind(b_bishop, "<Button-1>", mainframe_bar)
piece_pos(b_bishop)

# ! Rook Black Test
b_rook=canvas.create_image(
    0, 0,
    image=canvas.b_rook_image,
    tag=("rook","black","piece","A8"))

canvas.tag_bind(b_rook, "<Button-1>", mainframe_bar)
piece_pos(b_rook)

# ! Knight Black Test
b_knight=canvas.create_image(
    0, 0,
    image=canvas.b_knight_image,
    tag=("knight","black","piece","B8"))

canvas.tag_bind(b_knight, "<Button-1>", mainframe_bar)
piece_pos(b_knight)

# ! Rook Black Test 2
b_rook_2=canvas.create_image(
    0, 0,
    image=canvas.b_rook_image,
    tag=("rook","black","piece","H8"))

canvas.tag_bind(b_rook_2, "<Button-1>", mainframe_bar)
piece_pos(b_rook_2)

# ! Knight Black Test 2
b_knight_2=canvas.create_image(
    0,0,
    image=canvas.b_knight_image,
    tag=("knight","black","piece","G8"))

canvas.tag_bind(b_knight_2, "<Button-1>", mainframe_bar)
piece_pos(b_knight_2)

# ! Bishop Black Test 2
b_bishop_2=canvas.create_image(
    0,0,
    image=canvas.b_bishop_image,
    tag=("bishop","black","piece","F8"))

canvas.tag_bind(b_bishop_2, "<Button-1>", mainframe_bar)
piece_pos(b_bishop_2)

# ! ==========================================================================================
# ! Pawn BLACK
# ! ==========================================================================================

pawn_list_black=[]
for k in range(8):
    pawn_list_black.append(
        canvas.create_image(
            0, 0,
            image=canvas.b_pawn_image,
            tag=("pawn","black","piece",position_pawn_list_black[k],"True"))
    )
    canvas.tag_bind(pawn_list_black[k], "<Button-1>", mainframe_bar)
    piece_pos(pawn_list_black[k])

root.resizable(False, False)
root.mainloop()