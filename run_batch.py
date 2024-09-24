import argparse
import os
from GazeXR import (
    run_detection,
    reID,
    initialize_plot_data,
    generate_graph,
)
from video_annotator import VideoAnnotator


def process_video(video_path):
    # Step 1: Run detection on the video
    print(f"Running detection on video: {video_path}")
    output_path, results, rotate_amount = run_detection(video_path)

    # Step 2: ReID on the detected output
    print(f"Running reID on the detected video: {output_path}")
    json_path, video_results_path = reID(output_path, results, rotate_amount)

    return json_path

def process_folder(json_path, csv_folder):
    # Step 3: Loop through all CSV files in the folder
    for filename in os.listdir(csv_folder):
        if filename.endswith(".csv"):
            csv_path = os.path.join(csv_folder, filename)
            print(f"Processing CSV file: {csv_path}")

            # Step 4: Initialize plot data
            plot = initialize_plot_data(json_path, csv_path)

            # Step 5: Generate graph and save it
            graph_output_path = os.path.join(csv_folder, f"{os.path.splitext(filename)[0]}_graph.png")
            generate_graph(plot, graph_output_path)

            print(f"Graph generated and saved to: {graph_output_path}")
    print("All graphs generated successfully.")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process a video and generate graphs for each CSV in a folder.")
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("csv_folder", help="Path to the folder containing CSV files")
    
    # Parse arguments
    args = parser.parse_args()

    # Step 1: Process the video
    json_path = process_video(args.video)

    input("JSON file created. Press Enter to continue processing CSV files...")
    # Step 2: Process the folder with CSV files
    process_folder(json_path, args.csv_folder)

if __name__ == "__main__":
    main()
