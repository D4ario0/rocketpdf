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
from pdf2docx import Converter


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
def convert_pdf_docx(file: PDF, docx_path: Path) -> None:
    logging.getLogger().setLevel(logging.ERROR)  # Disable logging
    if isinstance(file, Path):
        validate_path(file)

    converter = Converter(str(file))
    converter.convert(str(docx_path))
    converter.close()
    return


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


# Function to chain arguments
@spinner(False)
def execute(args: List[str], file: bytes, output: Path = None) -> bytes | None:
    while args:
        next_command, arg = __get_expression(args)
        try:
            if next_command == "extract":
                start = int(arg[0])
                if len(arg) > 2:
                    raise ValueError(f"Invalid number of arguments for {next_command}")
                end = int(arg[1]) if len(arg) > 1 else None
                new_file = extract_pages(file, start, end)

            if next_command == "merge":
                new_file = merge_pdfs([file] + list(arg))

            if next_command == "compress":
                if arg and len(arg) > 0:
                    raise ValueError(f"Invalid number of arguments for {next_command}")
                new_file = compress_pdf(file)

            if next_command == "parsepdf":
                if arg and len(arg) > 1:
                    raise ValueError(f"Invalid number of arguments for {next_command}")
                output_path = Path(arg[0]) if arg else output.with_suffix(".docx")
                convert_pdf_docx(file, output_path)
                return

            return execute(args, new_file, output)
        except:
            return file
    return file


def __get_expression(args: List[str]) -> Tuple[str, Tuple[str | int | Path]]:
    commands = {"merge", "extract", "compress", "parsepdf"}
    command = args.pop(0)
    if command not in commands:
        raise ValueError("Not a valid command")

    expression = []
    while args and args[0] not in commands:
        expression.append(args.pop(0))
    return command, tuple(expression)
