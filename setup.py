from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="language_processing_tool",  # Keep underscores for readability
    version="0.2.7",
    packages=find_packages(include=["language_processing_tool", "language_processing_tool.*"]),  # Include sub-packages if any
    install_requires=[
        "pytesseract",
        "langdetect",
        "pandas",
        "PyMuPDF",
        "icecream",
        "Pillow"
    ],
    entry_points={
        'console_scripts': [
            'process-pdfs = language_processing_tool.process_pdfs:main',
        ],
    },
    description="A PDF language detection and OCR tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harish Kumar S",
    author_email="harishkumar56278@gmail.com",
    url="https://github.com/Harish-nika/language-processing-tool",
    license="MIT",  # Specify license
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,  # Ensures data files (if any) are included
)
