import json
import argparse
from GazeXR import convert_to_serializable

def swap_ids(bboxes, id1, id2, frame):
    """
    Swap IDs of the selected bounding boxes starting from a specific frame onward.

    :param bboxes: List of bounding boxes for all frames.
    :param id1: The first bounding box ID.
    :param id2: The second bounding box ID.
    :param frame: The specific frame number where the bounding boxes are selected.
    :return: Modified bounding boxes with swapped IDs from the given frame onward.
    """
    # Swap the IDs from the specified frame onward
    for frame_idx in range(frame, len(bboxes)):
        for bbox_dict in bboxes[frame_idx]:
            if bbox_dict["id"] == id1:
                bbox_dict["id"] = id2
            elif bbox_dict["id"] == id2:
                bbox_dict["id"] = id1

    return bboxes

def remove_boxes_by_id(bboxes, bbox_id, start_frame, end_frame=None):
    """
    Remove all bounding boxes with a specific ID over a specified range of frames.

    :param bboxes: List of bounding boxes for all frames.
    :param bbox_id: The bounding box ID to remove.
    :param start_frame: The starting frame number for removal.
    :param end_frame: The ending frame number for removal (if None, remove to the end).
    :return: Modified bounding boxes with the specified ID removed.
    """
    # If no end_frame is specified, remove boxes from start_frame to the end of the frames list
    if end_frame is None or end_frame >= len(bboxes):
        end_frame = len(bboxes) - 1

    # Remove the boxes with the given ID over the specified range
    for frame_idx in range(start_frame, end_frame + 1):
        bboxes[frame_idx] = [bbox for bbox in bboxes[frame_idx] if bbox["id"] != bbox_id]

    return bboxes

def load_bboxes(file_path):
    with open(file_path, 'r') as file:
        boxes_for_gaze = json.load(file)

    rotation = boxes_for_gaze.get("rotate_amount", 0)
    boxes_for_gaze = boxes_for_gaze.get("boxes", [])
    return boxes_for_gaze, rotation

def save_bboxes(file_path, boxes_for_gaze, rotate_amount=0):
    """Save bounding boxes to a JSON file."""
    dump_boxes_with_rotate = {
        "boxes": boxes_for_gaze,
        "rotate_amount": rotate_amount
    }
    dump_boxes_with_rotate = convert_to_serializable(dump_boxes_with_rotate)
    with open(file_path, 'w') as file:
        json.dump(dump_boxes_with_rotate, file, indent=4)
        
def main():
    # Load the JSON file
    json_file = "bounding_boxes_rotated_Molnar_M_Amb_Clip2_logo.json"

    # Load bounding boxes
    bboxes, rotation = load_bboxes(json_file)

    while True:
        # Prompt user for the operation type
        print("Select an operation:")
        print("1. Swap IDs")
        print("2. Remove bounding boxes by ID over a range")
        operation = input("Enter 1 or 2: ").strip()

        if operation == '1':
            # Swap IDs
            id1 = int(input("Enter the first bounding box ID to swap: "))
            id2 = int(input("Enter the second bounding box ID to swap: "))
            frame = int(input("Enter the frame number: "))

            # Perform the ID swap
            bboxes = swap_ids(bboxes, id1, id2, frame)
            print(f"Swapped IDs {id1} and {id2} for frame {frame} and onward.")

        elif operation == '2':
            # Remove bounding boxes by ID over a range
            bbox_id = int(input("Enter the bounding box ID to remove: "))
            start_frame = int(input("Enter the starting frame number: "))
            end_frame_input = input("Enter the ending frame number (or type 'end' to remove until the last frame): ").strip()

            # Determine the end frame
            end_frame = None if end_frame_input.lower() == 'end' else int(end_frame_input)

            # Remove the boxes with the given ID over the specified range
            bboxes = remove_boxes_by_id(bboxes, bbox_id, start_frame, end_frame)
            print(f"Removed bounding boxes with ID {bbox_id} from frame {start_frame} to {end_frame if end_frame is not None else 'the end'}.")

        else:
            print("Invalid operation selected. Please try again.")

        # Save the updated bounding boxes back to the file
        save_bboxes(json_file, bboxes, rotation)

        # Ask the user if they want to continue or stop
        continue_operation = input("Do you want to perform another operation? (y/n): ").strip().lower()
        if continue_operation != 'y':
            break

if __name__ == "__main__":
    main()
