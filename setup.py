from setuptools import setup, find_packages
setup(
    name="language_processing_tool",  # Use underscores here
    version="0.2.6",  # Increment the version
    packages=find_packages(),
    install_requires=[
        "pytesseract",
        "langdetect",
        "pandas",
        "PyMuPDF",
        "icecream",
        "Pillow",
        "argparse",
    ],
    entry_points={
        'console_scripts': [
            'process-pdfs = language_processing_tool.process_pdfs:main',
        ],
    },
    description="A PDF language detection and OCR tool",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Harish Kumar S",
    author_email="harishkumar56278@gmail.com",
    url="https://github.com/Harish-nika/language-processing-tool",  # Update this if needed
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
