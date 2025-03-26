__version__ = '0.2.7'

import os
import fitz  # PyMuPDF for PDF handling
import pandas as pd
import re
import pytesseract
import argparse
import signal  # For handling manual interruptions
from langdetect import detect, DetectorFactory
from collections import defaultdict
from PIL import Image
from multiprocessing import Pool
from datetime import datetime

# Disable Icecream debug output
from icecream import ic
ic.disable()

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Update path if needed
DetectorFactory.seed = 0

CHECKPOINT_FILE = "checkpoint.xlsx"  # Temporary checkpoint file

# Function to extract text from PDFs (OCR for scanned PDFs)
def extract_text_from_pdf(pdf_path):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File {pdf_path} does not exist.")
    
    pdf_document = fitz.open(pdf_path)
    text_chunks = []
    is_scanned = False
    
    for page in pdf_document:
        text = page.get_text("text")
        
        if not text:  # If empty, likely a scanned document
            is_scanned = True
            img = Image.frombytes("RGB", [page.get_pixmap().width, page.get_pixmap().height], page.get_pixmap().samples)
            text = pytesseract.image_to_string(img)
        
        text_chunks.append(re.sub(r'[^\x00-\x7F]+', ' ', text))  # Remove non-ASCII characters
    
    pdf_document.close()
    return text_chunks, is_scanned

# Function to detect languages and compute percentages
def detect_languages(text_chunks):
    language_counts = defaultdict(int)
    for text in text_chunks:
        try:
            language_counts[detect(text)] += 1
        except:
            continue
    
    total_chunks = len(text_chunks)
    language_percentages = {lang: (count / total_chunks) * 100 for lang, count in language_counts.items()}
    dominant_language = max(language_percentages, key=language_percentages.get, default=None)
    
    return dominant_language, language_percentages

# Function to save results as an Excel checkpoint
def save_checkpoint(results, output_path):
    pd.DataFrame(results, columns=['Filename', 'Document Number', 'Dominant Language', 'Language Distribution', 'Is Scanned']) \
        .to_excel(output_path, index=False)

# Worker function for processing a single PDF
def process_single_pdf(pdf_info):
    index, filename, pdf_path = pdf_info
    try:
        print(f"Processing Document {index + 1}: {pdf_path}")
        text_chunks, is_scanned = extract_text_from_pdf(pdf_path)
        dominant_language, language_percentages = detect_languages(text_chunks)
        return [filename, index + 1, dominant_language, language_percentages, is_scanned]
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

# Function to process multiple PDFs in parallel
def process_pdfs(input_folder, csv_file, output_dir, num_processes=4):
    os.makedirs(output_dir, exist_ok=True)
    checkpoint_path = os.path.join(output_dir, CHECKPOINT_FILE)
    
    # Read filenames from CSV
    filenames_df = pd.read_csv(csv_file)
    pdf_infos = [(index, row['filename'], os.path.join(input_folder, f"{row['filename']}.pdf")) for index, row in filenames_df.iterrows()]
    
    # Load existing checkpoint if available
    processed_filenames = set(pd.read_excel(checkpoint_path)['Filename']) if os.path.exists(checkpoint_path) else set()
    unprocessed_pdf_infos = [pdf for pdf in pdf_infos if pdf[1] not in processed_filenames]
    
    # Signal handling for graceful termination
    def save_and_exit(signum, frame):
        print("Interrupt received. Saving progress...")
        save_checkpoint(results, checkpoint_path)
        exit(0)
    
    signal.signal(signal.SIGINT, save_and_exit)
    signal.signal(signal.SIGTERM, save_and_exit)
    
    # Process PDFs in parallel
    results = []
    with Pool(num_processes) as pool:
        for result in pool.imap(process_single_pdf, unprocessed_pdf_infos):
            if result:
                results.append(result)
                save_checkpoint(results, checkpoint_path)
    
    # Save final results
    final_output_path = os.path.join(output_dir, f"language_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    save_checkpoint(results, final_output_path)
    print(f"Processing completed. Results saved to {final_output_path}")

# Function to process a single PDF
def process_single_file(pdf_path):
    print(f"Processing single file: {pdf_path}")
    text_chunks, is_scanned = extract_text_from_pdf(pdf_path)
    return detect_languages(text_chunks) + (is_scanned,)

# Argument parsing
def main():
    parser = argparse.ArgumentParser(description="PDF Language Detection and OCR")
    parser.add_argument("input", help="Input folder or PDF file path")
    parser.add_argument("csv_file", help="CSV file containing PDF filenames", nargs='?', default=None)
    parser.add_argument("output", help="Output directory for results", nargs='?', default=None)
    parser.add_argument("num_processes", help="Number of processes", type=int, nargs='?', default=4)
    
    args = parser.parse_args()
    
    if args.csv_file and args.output:
        process_pdfs(args.input, args.csv_file, args.output, args.num_processes)
    else:
        print(process_single_file(args.input))

if __name__ == "__main__":
    main()
