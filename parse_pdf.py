import os
import json
import re
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self, input_folder: str = r"..\Worship musiek"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path("parsed_songs")
        self.output_folder.mkdir(exist_ok=True)
        
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """Extract text from PDF file using available PDF libraries."""
        try:
            # Try pdfplumber first (better for complex layouts)
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text.strip()
            except ImportError:
                logger.warning("pdfplumber not available, trying PyPDF2")
                
            # Fallback to PyPDF2
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
            except ImportError:
                logger.error("Neither pdfplumber nor PyPDF2 is installed")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def parse_song_content(self, text: str, filename: str) -> Dict[str, Any]:
        """Parse the extracted text into structured song data."""
        song_data = {
            "filename": filename,
            "title": "",
            "artist": "",
            "lyrics": [],
            "chords": [],
            "metadata": {},
            "raw_text": text
        }
        
        if not text:
            return song_data
        
        lines = text.split('\n')
        
        # Try to extract title (usually first non-empty line)
        for line in lines:
            line = line.strip()
            if line and not line.startswith('©') and not line.startswith('Chords:'):
                song_data["title"] = line
                break
        
        # Extract lyrics and chords
        current_section = "lyrics"
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip copyright and metadata lines
            if line.startswith('©') or line.startswith('Chords:'):
                continue
                
            # Check if line contains chord patterns (capital letters followed by numbers/symbols)
            if re.search(r'\b[A-G][#b]?(?:m|maj|min|dim|aug|sus)?[0-9]?\b', line):
                song_data["chords"].append(line)
            else:
                song_data["lyrics"].append(line)
        
        return song_data
    
    def save_to_json(self, song_data: Dict[str, Any], output_path: Path):
        """Save song data to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(song_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved: {output_path}")
        except Exception as e:
            logger.error(f"Error saving {output_path}: {e}")
    
    def process_pdf(self, pdf_path: Path) -> bool:
        """Process a single PDF file."""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)
            if text is None:
                return False
            
            # Parse the content
            song_data = self.parse_song_content(text, pdf_path.stem)
            
            # Create output filename
            output_filename = f"{pdf_path.stem}.json"
            output_path = self.output_folder / output_filename
            
            # Save to JSON
            self.save_to_json(song_data, output_path)
            return True
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return False
    
    def process_all_pdfs(self) -> Dict[str, int]:
        """Process all PDF files in the input folder."""
        if not self.input_folder.exists():
            logger.error(f"Input folder does not exist: {self.input_folder}")
            return {"processed": 0, "failed": 0, "total": 0}
        
        pdf_files = list(self.input_folder.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.input_folder}")
            return {"processed": 0, "failed": 0, "total": 0}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        processed = 0
        failed = 0
        
        for pdf_file in pdf_files:
            if self.process_pdf(pdf_file):
                processed += 1
            else:
                failed += 1
        
        return {
            "processed": processed,
            "failed": failed,
            "total": len(pdf_files)
        }

def main():
    """Main function to run the PDF parser."""
    parser = PDFParser()
    
    logger.info("Starting PDF parsing process...")
    results = parser.process_all_pdfs()
    
    logger.info("Parsing completed!")
    logger.info(f"Total files: {results['total']}")
    logger.info(f"Successfully processed: {results['processed']}")
    logger.info(f"Failed: {results['failed']}")
    
    if results['processed'] > 0:
        logger.info(f"JSON files saved to: {parser.output_folder.absolute()}")

if __name__ == "__main__":
    main()
