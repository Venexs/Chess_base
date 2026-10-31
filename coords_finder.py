import json

def get_center_from_key(json_path, key):
    with open(json_path, "r") as f:
        data = json.load(f)

    if key not in data:
        raise KeyError(f"{key} not found in JSON")

    x1, y1, x2, y2 = data[key]
    avg_x = (x1 + x2) / 2
    avg_y = (y1 + y2) / 2

    return avg_x, avg_y

pos_in=input("Position: ")

center_x, center_y = get_center_from_key("positions_val.json", pos_in)
print(center_x, center_y)
