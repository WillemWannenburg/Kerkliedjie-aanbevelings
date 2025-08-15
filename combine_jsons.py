import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def combine_json_files(input_folder: str = "parsed_songs", output_file: str = "combined_songs.json"):
    """
    Combine all JSON files from the input folder into a single JSON file.
    Keeps only filename and lyrics from each song.
    """
    input_path = Path(input_folder)
    output_path = Path(output_file)
    
    # Check if input folder exists
    if not input_path.exists():
        logger.error(f"Input folder does not exist: {input_path}")
        return False
    
    # Find all JSON files
    json_files = list(input_path.glob("*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in {input_path}")
        return False
    
    logger.info(f"Found {len(json_files)} JSON files to combine")
    
    combined_data = []
    
    for json_file in json_files:
        try:
            logger.info(f"Processing: {json_file}")
            
            # Read JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                song_data = json.load(f)
            
            # Extract only filename and lyrics
            simplified_song = {
                "filename": song_data.get("filename", json_file.stem),
                "lyrics": song_data.get("lyrics", [])
            }
            
            combined_data.append(simplified_song)
            
        except Exception as e:
            logger.error(f"Error processing {json_file}: {e}")
            continue
    
    # Save combined data to output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully combined {len(combined_data)} songs into {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving combined file: {e}")
        return False

def main():
    """Main function to run the JSON combiner."""
    logger.info("Starting JSON combination process...")
    
    success = combine_json_files()
    
    if success:
        logger.info("JSON combination completed successfully!")
    else:
        logger.error("JSON combination failed!")

if __name__ == "__main__":
    main()
