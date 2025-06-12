import fitz

from .clitools import spinner
from .converter import LOCAL_ENGINE, ConverterEngine
from .utils.io import handle_range


@spinner("Converting docx to pdf file")
def docx_to_pdf(in_file: str, out_file: str, converter: ConverterEngine = LOCAL_ENGINE()) -> None:
    converter.docx_to_pdf(in_file, out_file)


@spinner("Converting pdf to docx file")
def pdf_to_docx(in_file: str, out_file: str, converter: ConverterEngine = LOCAL_ENGINE()) -> None:
    converter.pdf_to_docx(in_file, out_file)


@spinner("Converting pdf to pptx file")
def pptx_to_pdf(in_file: str, out_file: str, converter: ConverterEngine = LOCAL_ENGINE()) -> None:
    converter.pptx_to_pdf(in_file, out_file)


@spinner("Converting pdf to xlsx file")
def xlsx_to_pdf(in_file: str, out_file: str, converter: ConverterEngine = LOCAL_ENGINE()) -> None:
    converter.xlsx_to_pdf(in_file, out_file)


@spinner("Extracting pages")
def extract_pages(in_file: str, start: int, end: int, out_file: str = None) -> None:
    with fitz.open(in_file) as file_to_extract:
        bounds = handle_range(start, end, len(file_to_extract) + 1)

        with fitz.open() as new_file:
            new_file.insert_pdf(file_to_extract, *bounds)
            new_file.save(out_file)


@spinner("Compressing PDF")
def compress_pdf(in_file: str, out_file: str = None, compress_img: bool = True) -> None:
    new_filename = out_file or f"{in_file}-compressed"

    with fitz.open(in_file) as file_to_compress:
        with fitz.open() as new_file:
            new_file.insert_pdf(file_to_compress)

            new_file.save(new_filename, garbage=3, deflate=True, deflate_images=compress_img)


@spinner("Merging PDFs")
def merge_pdfs(input_files: tuple[str, ...], out_file: str) -> None:
    """
    Merges multiple PDF files into a single PDF.

    :param input_files: A tuple of filenames to merge.
    :param out_file: The name of the output merged PDF file.
    """
    with fitz.open() as merged_file:
        for pdf_file in input_files:
            with fitz.open(pdf_file) as file_to_merge:
                merged_file.insert_pdf(file_to_merge)
        merged_file.save(out_file)
