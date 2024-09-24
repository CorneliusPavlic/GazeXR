
import json
import argparse

def swap_ids(bboxes, id1, id2, frame):
    """
    Swap IDs of the selected bounding boxes for all frames.

    :param bboxes: List of bounding boxes for all frames.
    :param id1: The first bounding box ID.
    :param id2: The second bounding box ID.
    :param frame: The specific frame number where the bounding boxes are selected.
    :return: Modified bounding boxes with swapped IDs.
    """
    # Swap the IDs in all frames where the IDs are present
    for frame_idx in range(len(bboxes)):
        for bbox_dict in bboxes[frame_idx]:
            if bbox_dict["id"] == id1:
                bbox_dict["id"] = id2
            elif bbox_dict["id"] == id2:
                bbox_dict["id"] = id1

    return bboxes

def load_bboxes(file_path):
    """Load bounding boxes from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_bboxes(file_path, bboxes):
    """Save bounding boxes to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(bboxes, file, indent=4)

def main():
    # # Set up argument parsing for the JSON file path
    # parser = argparse.ArgumentParser(description="Swap bounding box IDs in all frames for a given frame.")
    # parser.add_argument("json_file", help="Path to the JSON file containing bounding boxes.")
    
    # Parse arguments
    # args = parser.parse_args()
    json_file = "bounding_boxes.json"
    # Load bounding boxes
    bboxes = load_bboxes(json_file)

    while True:
        # Prompt the user for the IDs and frame number
        id1 = int(input("Enter the first bounding box ID to swap: "))
        id2 = int(input("Enter the second bounding box ID to swap: "))
        frame = int(input("Enter the frame number: "))

        # Perform the ID swap
        bboxes = swap_ids(bboxes, id1, id2, frame)

        # Save the updated bounding boxes back to the file
        save_bboxes(json_file, bboxes)

        print(f"Swapped IDs {id1} and {id2} for frame {frame} and saved to {json_file}")

        # Ask the user if they want to continue or stop
        continue_swap = input("Do you want to swap more IDs? (y/n): ").strip().lower()
        if continue_swap != 'y':
            break

if __name__ == "__main__":
    main()
