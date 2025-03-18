__version__ = '0.2.6'

import os
import fitz  # PyMuPDF for PDF handling
import pandas as pd
import re
import pytesseract
from langdetect import detect, DetectorFactory
from icecream import ic
from collections import defaultdict
from PIL import Image
from multiprocessing import Pool, Manager
from datetime import datetime
import signal  # For handling manual interruptions
import argparse  # For argument parsing

# Disable Icecream debug output
ic.disable()

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Update Tesseract path
DetectorFactory.seed = 0

checkpoint_file = "checkpoint.xlsx"  # Temporary file for checkpointing

# Function to extract text using Tesseract OCR from image-based PDFs
def extract_text_from_pdf(pdf_path):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File {pdf_path} does not exist.")
    
    pdf_document = fitz.open(pdf_path)
    text_chunks = []
    is_scanned = False
    
    for page_num, page in enumerate(pdf_document):
        # Try to extract text directly
        text = page.get_text("text")
        
        if not text:  # If no text, it's likely scanned
            is_scanned = True
            # Use OCR for scanned pages
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
        
        text_cleaned = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        text_chunks.append(text_cleaned)
    
    pdf_document.close()
    return text_chunks, is_scanned

# Function to detect languages and compute percentages
def detect_languages(text_chunks):
    language_counts = defaultdict(int)
    for text_chunk in text_chunks:
        try:
            detected_lang = detect(text_chunk)
            language_counts[detected_lang] += 1
        except:
            continue
    
    total_chunks = len(text_chunks)
    language_percentages = {lang: (count / total_chunks) * 100 for lang, count in language_counts.items()}
    dominant_language = max(language_percentages, key=language_percentages.get) if language_percentages else None
    
    return dominant_language, language_percentages

# Function to save intermediate results to an Excel file
def save_checkpoint(results, output_path):
    df = pd.DataFrame(results, columns=['Filename', 'Document Number', 'Dominant Language', 'Language Distribution', 'Is Scanned'])
    df.to_excel(output_path, index=False)

# Worker function to process a single PDF
def process_single_pdf(pdf_info):
    index, filename, pdf_path = pdf_info
    try:
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"File {pdf_path} does not exist.")
        
        print(f"Processing Document {index + 1}: {pdf_path}")

        # Extract text from the PDF and determine if it's scanned
        text_chunks, is_scanned = extract_text_from_pdf(pdf_path)
        ic(text_chunks)

        # Detect languages and calculate percentages
        dominant_language, language_percentages = detect_languages(text_chunks)

        # Display results
        print(f"Document {index + 1}: {filename}")
        print(f"Dominant Language: {dominant_language}")
        for lang, percentage in language_percentages.items():
            print(f"- {lang}: {percentage:.2f}%")
        print(f"Is Scanned: {is_scanned}")

        # Return the result for Excel
        return [filename, index + 1, dominant_language, language_percentages, is_scanned]

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred for Document {index + 1}: {e}")
    return None

# Main function to process all PDFs and save results
def process_pdfs(input_folder, csv_file, output_dir, num_processes=4):
    results = []  # To store the results for Excel
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    checkpoint_path = os.path.join(output_dir, checkpoint_file)

    # Read the CSV file with filenames
    filenames_df = pd.read_csv(csv_file)
    pdf_infos = [(index, row['filename'], os.path.join(input_folder, f"{row['filename']}.pdf")) for index, row in filenames_df.iterrows()]

    # Load existing checkpoint if available
    if os.path.exists(checkpoint_path):
        processed_df = pd.read_excel(checkpoint_path)
        processed_filenames = set(processed_df['Filename'])
        print(f"Resuming from checkpoint. {len(processed_filenames)} files already processed.")
    else:
        processed_filenames = set()

    # Filter only unprocessed files
    unprocessed_pdf_infos = [pdf_info for pdf_info in pdf_infos if pdf_info[1] not in processed_filenames]

    # Graceful interruption handling
    def save_and_exit(signum, frame):
        print("Interrupt received. Saving progress...")
        save_checkpoint(results, checkpoint_path)
        exit(0)

    signal.signal(signal.SIGINT, save_and_exit)
    signal.signal(signal.SIGTERM, save_and_exit)

    # Process PDFs in parallel
    with Pool(num_processes) as pool:
        for result in pool.imap(process_single_pdf, unprocessed_pdf_infos):
            if result:
                results.append(result)
                save_checkpoint(results, checkpoint_path)  # Save after every processed PDF

    # Save final results to Excel
    final_output_path = os.path.join(output_dir, f"language_distribution_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    save_checkpoint(results, final_output_path)
    print(f"Processing completed. Results saved to {final_output_path}")

# Function to handle the single file scenario
def process_single_file(pdf_path):
    print(f"Processing single file: {pdf_path}")
    text_chunks, is_scanned = extract_text_from_pdf(pdf_path)
    
    # Detect languages and calculate percentages
    dominant_language, language_percentages = detect_languages(text_chunks)

    # Display results
    print(f"Dominant Language: {dominant_language}")
    for lang, percentage in language_percentages.items():
        print(f"- {lang}: {percentage:.2f}%")
    print(f"Is Scanned: {is_scanned}")

# Argument parsing logic
def main():
    parser = argparse.ArgumentParser(description="PDF Language Detection and OCR")
    parser.add_argument("input", help="Input folder or PDF file path")
    parser.add_argument("csv_file", help="CSV file containing PDF filenames", nargs='?', default=None)
    parser.add_argument("output", help="Output directory for saving results", nargs='?', default=None)
    parser.add_argument("num_processes", help="Number of processes to use", type=int, nargs='?', default=4)
    
    args = parser.parse_args()

    if args.csv_file and args.output:  # Process all PDFs in the folder
        input_folder = args.input
        csv_file = args.csv_file
        output_dir = args.output
        num_processes = args.num_processes
        
        process_pdfs(input_folder, csv_file, output_dir, num_processes)

    else:  # Process a single PDF
        pdf_path = args.input
        process_single_file(pdf_path)

if __name__ == "__main__":
    main()
