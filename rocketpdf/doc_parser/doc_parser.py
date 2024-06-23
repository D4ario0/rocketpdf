import logging
from os import environ
from pathlib import Path
from typing import List, Tuple
from multiprocessing import Pool
from .utils import *

# Disable tqdm progress bar
environ["TQDM_DISABLE"] = "1"

# Third-party library imports
import fitz
import docx2pdf
from pdf2docx import parse


@spinner("Converting DOCX to PDF...", "DOCX converted successfully")
def convert_docx_pdf(file_path: Path) -> bytes:
    if OP_S == "Linux":
        raise NotImplementedError("Conversion not supported on Linux.")

    validate_path(file_path)

    temp_path = file_path.parent / f"{HIDDEN_PREFIX}temp.pdf"

    docx2pdf.convert(file_path, temp_path)

    if OP_S == "Windows":
        win32file.SetFileAttributes(str(temp_path), 2)

    with open(temp_path, "rb") as file:
        byte_stream = file.read()

    remove_temp(temp_path)
    return byte_stream


@spinner("Converting PDF to DOCX...", "PDF converted successfully")
def convert_pdf_docx(file_path: Path, docx_path: Path) -> None:
    logging.getLogger().setLevel(logging.ERROR)  # Disable logging

    validate_path(file_path)

    parse(file_path, docx_path)


@spinner("Merging PDFs...", "PDFs merged successfully")
def merge_pdfs(pdf_list: List[PDF]) -> bytes:
    for pdf in pdf_list:
        if isinstance(pdf, Path):
            validate_path(pdf)

    with fitz.open() as new_file:
        for pdf in pdf_list:
            with to_PDF(pdf) as pdf_doc:
                new_file.insert_pdf(pdf_doc)
        return new_file.tobytes()


@spinner("Extracting pages from PDF...", "PDF pages extracted successfully")
def extract_pages(file: PDF, start: int, end: int = None) -> bytes:
    if isinstance(file, Path):
        validate_path(file)
    end = end or start
    with fitz.open() as new_file:
        with to_PDF(file) as temp:
            if start < 1 or end > len(temp):
                raise ValueError("Invalid page range specified.")
            new_file.insert_pdf(temp, from_page=start - 1, to_page=end - 1)
        return new_file.tobytes()


def __convert_pdf_txt(file: PDF) -> str:
    content = ""
    with to_PDF(file) as doc:
        for page in doc:
            output = page.get_text("blocks")
            previous_block_id = 0
            for block in output:
                if block[6] == 0:
                    if previous_block_id != block[5]:
                        content += "\n"
                    content += block[4]
    return content


@spinner("Compressing PDF...", "PDF compressed successfully")
def compress_pdf(file: PDF) -> bytes:
    if isinstance(file, Path):
        validate_path(file)

    with to_PDF(file) as new_file:
        return new_file.tobytes(deflate=True, garbage=4)


@spinner("Converting files...", "DOCX in directory converted successfully")
def parse_dir(path: Path) -> None:
    if OP_S == "Linux":
        raise NotImplementedError("Conversion not supported on Linux.")

    validate_path(path)

    docxlist = [file for file in path.iterdir() if file.suffix == ".docx"]

    with Pool() as pool:
        pool.map(docx2pdf.convert, docxlist)

    return


def merge_dir(path: Path) -> bytes:
    validate_path(path)

    pdflist = [file for file in path.iterdir() if file.suffix == ".pdf"]
    return merge_pdfs(pdflist)


# Command chaining variables and functions
COMMANDS = {
    "extract": extract_pages,
    "merge": merge_pdfs,
    "compress": lambda file, *args: compress_pdf(file),
}


# Function to chain arguments
def execute(params: List[str], file: PDF, output: Path = None) -> bytes | None:
    try:
        if params:
            next_command, args = __next_command(params)
            new_file = COMMANDS[next_command](file, *args)
            return execute(params, new_file, output)
        return file
    except:
        return file


# Funtion to extract chained expressions
def __next_command(params: List[str]) -> Tuple[str, Tuple]:
    command = params.pop(0)
    if command not in COMMANDS:
        raise ValueError("Not a valid command")

    if command == "extract":
        try:
            start = int(params.pop(0))
            end = int(params.pop(0)) if params and params[0] not in COMMANDS else start
        except TypeError:
            raise ValueError(f"Invalid range argument for {command}")
        return command, (start, end)

    if command == "merge":
        sep = find_non_pdf(params)
        pdflist = [Path(params.pop(0)) for _ in range(sep)]
        if not pdflist:
            raise ValueError(f"No file given for {command}")
        return command, tuple(pdflist)

    return command, tuple()


# Function to find next argument
def find_non_pdf(params: List[str]) -> int:
    n = len(params)
    for i in range(n):
        if not params[i].endswith(".pdf"):
            return i
    return n
