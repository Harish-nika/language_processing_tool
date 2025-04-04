# Language Processing Tool

**Language Processing Tool** is a Python package that processes PDFs and detects languages in documents. It supports both text-based and scanned PDFs using OCR.

## Installation

You can install the package from PyPI using:

```sh
pip install language-processing-tool
```

## Features

- Extracts text from PDFs (both text-based and scanned).
- Uses OCR (Tesseract) for image-based PDFs.
- Detects the dominant language and provides a language distribution.
- Supports batch processing of multiple PDFs.
- CLI and programmatic usage available.

## Usage

### **In Python Code**

To use this package in your Python script:

```python
from language_processing_tool.process_pdfs import process_pdfs, process_single_file

# Process a single PDF file
print(process_single_file("/path/to/file.pdf"))

# Process multiple PDFs from a directory (using CSV input)
process_pdfs("/path/to/input_folder/", "pdf_files.csv", "/path/to/output_folder/")
```

### **Command Line Usage**

After installing the package, you can use the CLI tool:

#### **Process a Single PDF**

```sh
process-pdfs /path/to/file.pdf
```

#### **Batch Processing (Using CSV)**

```sh
process-pdfs /path/to/input_folder/ /path/to/csv_file.csv /path/to/output_folder/
```

### **CSV File Format**

The CSV file should contain a column named **filename**, listing the PDF filenames (without extensions). Example:

```csv
filename
document1
document2
document3
```

Make sure the corresponding PDFs (`document1.pdf`, `document2.pdf`, etc.) are in the specified input folder.

## Project Structure

```
language_processing_tool
├── LICENSE
├── README.md
├── setup.py
├── pyproject.toml
├── requirements.txt
├── language_processing_tool
│   ├── __init__.py
│   ├── process_pdfs.py
│   ├── sourcecode.py
├── tests
│   ├── test.py
```

## Entry Points

The package includes a CLI entry point:

```sh
process-pdfs <arguments>
```

which maps to the `main()` function in `process_pdfs.py`.

## Dependencies

This package requires:

- `pytesseract`
- `langdetect`
- `pandas`
- `PyMuPDF`
- `icecream`
- `Pillow`
- `argparse`

## License

This project is licensed under the **MIT License**.

## Author

- **Harish Kumar S**
- GitHub: [Harish-nika](https://github.com/Harish-nika)
- Email: [harishkumar56278@gmail.com](mailto\:harishkumar56278@gmail.com)
- portfolio: [Harish Kumar S - AI ML Engineer](https://harish-nika.github.io/)

