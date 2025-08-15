import json
import logging
from pathlib import Path
from typing import List, Set

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_played_file(played_file: str = "Played.txt") -> Set[str]:
    """
    Remove duplicates from Played.txt and return a set of unique filenames.
    """
    played_path = Path(played_file)
    
    if not played_path.exists():
        logger.error(f"Played.txt file not found: {played_path}")
        return set()
    
    try:
        # Read all lines from Played.txt
        with open(played_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        logger.info(f"Read {len(lines)} lines from {played_file}")
        
        # Clean and deduplicate filenames
        unique_filenames = set()
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace and remove file extensions
            filename = line.strip()
            if filename:
                # Remove common file extensions if present
                for ext in ['.pdf', '.txt', '.json']:
                    if filename.endswith(ext):
                        filename = filename[:-len(ext)]
                        break
                
                if filename not in unique_filenames:
                    unique_filenames.add(filename)
                    cleaned_lines.append(filename)
        
        # Write back the cleaned file
        with open(played_path, 'w', encoding='utf-8') as f:
            for filename in sorted(cleaned_lines):
                f.write(filename + '\n')
        
        logger.info(f"Cleaned {played_file}: removed {len(lines) - len(cleaned_lines)} duplicates")
        logger.info(f"Kept {len(cleaned_lines)} unique filenames")
        
        return unique_filenames
        
    except Exception as e:
        logger.error(f"Error processing {played_file}: {e}")
        return set()

def filter_songs_json(played_filenames: Set[str], songs_file: str = "combined_songs.json") -> bool:
    """
    Filter combined_songs.json to keep only songs that are in the played list.
    """
    songs_path = Path(songs_file)
    
    if not songs_path.exists():
        logger.error(f"Songs file not found: {songs_path}")
        return False
    
    try:
        # Load the songs data
        with open(songs_path, 'r', encoding='utf-8') as f:
            songs = json.load(f)
        
        logger.info(f"Loaded {len(songs)} songs from {songs_file}")
        
        # Filter songs to keep only those in played_filenames
        filtered_songs = []
        removed_count = 0
        
        for song in songs:
            filename = song.get('filename', '')
            if filename in played_filenames:
                filtered_songs.append(song)
            else:
                removed_count += 1
        
        # Create backup of original file
        backup_path = songs_path.with_suffix('.json.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(songs, f, indent=2, ensure_ascii=False)
        logger.info(f"Created backup: {backup_path}")
        
        # Write filtered songs back to file
        with open(songs_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_songs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Filtered {songs_file}: kept {len(filtered_songs)} songs, removed {removed_count} songs")
        
        return True
        
    except Exception as e:
        logger.error(f"Error filtering {songs_file}: {e}")
        return False

def main():
    """Main function to clean played file and filter songs."""
    logger.info("Starting song filtering process...")
    
    # Step 1: Clean Played.txt and get unique filenames
    logger.info("Step 1: Cleaning Played.txt...")
    played_filenames = clean_played_file()
    
    if not played_filenames:
        logger.error("No filenames found in Played.txt. Exiting.")
        return
    
    # Step 2: Filter combined_songs.json
    logger.info("Step 2: Filtering combined_songs.json...")
    success = filter_songs_json(played_filenames=played_filenames)
    
    if success:
        logger.info("✅ Song filtering completed successfully!")
        logger.info(f"Final dataset contains songs that are in Played.txt")
    else:
        logger.error("❌ Song filtering failed!")

if __name__ == "__main__":
    main()