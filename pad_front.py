import json
from GazeXR import convert_to_serializable

with open('bounding_boxes_rotated_Molnar_M_Amb_Clip2_logo.json', 'r') as file:
        boxes_for_gaze = json.load(file)

rotation = boxes_for_gaze.get("rotate_amount", 0)
boxes_for_gaze = boxes_for_gaze.get("boxes", [])
for i in range(120):
    boxes_for_gaze.insert(0, [])
    
dump_boxes_with_rotate = {
        "boxes": boxes_for_gaze,
        "rotate_amount": rotation
            }
dump_boxes_with_rotate = convert_to_serializable(dump_boxes_with_rotate)
with open('bounding_boxes_rotated_Molnar_M_Amb_Clip2_logo.json', 'w') as file:
    json.dump(dump_boxes_with_rotate, file, indent=4)