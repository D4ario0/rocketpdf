import os
import fitz
import concurrent.futures
from io import BytesIO
from platform import system
from docx2pdf import convert
from typing import Union, List
from pdf2docx import Converter


try:
    import win32file
except ImportError:
    win32file = None

__OP_S = system()
__HIDDEN_PREFIX = "~$" if __OP_S == "Windows" else "."

PDF = Union[str, bytes]


def __to_byte_stream(doc: fitz.Document) -> bytes:
    with BytesIO() as buffer:
        doc.save(buffer)
        byte_stream = buffer.getvalue()
    return byte_stream


def __clean_up(temp_path: str) -> None:
    try:
        os.remove(temp_path)
    except Exception as e:
        print(f"Error cleaning up temporary file: {e}")


def to_PDF(file: PDF) -> fitz.Document:
    if isinstance(file, str):
        doc = fitz.open(file)
    elif isinstance(file, bytes):
        doc = fitz.open("pdf", file)
    else:
        raise ValueError("Input data must be a file path or bytes.")
    return doc


def convert_docx_pdf(file_path: str) -> bytes:
    if __OP_S == "Linux":
        raise NotImplementedError("Conversion not supported on Linux.")

    temp_path = f"{__HIDDEN_PREFIX}temp.pdf"

    convert(file_path, temp_path)

    if __OP_S == "Windows":
        win32file.SetFileAttributes(temp_path, 2)

    with open(temp_path, "rb") as file:
        byte_stream = file.read()

    __clean_up(temp_path)
    return byte_stream


def convert_pdf_docx(file: PDF, docx_path: str) -> None:
    with Converter(file) as converter:
        converter.convert(docx_path)


def merge_pdfs(pdf_list: List[PDF]) -> bytes:
    with fitz.open() as new_file:
        for pdf in pdf_list:
            with to_PDF(pdf) as pdf_doc:
                new_file.insert_pdf(pdf_doc)
        return __to_byte_stream(new_file)


def extract_pages(file: PDF, start: int, end: int) -> bytes:
    with fitz.open() as new_file:
        with to_PDF(file) as temp:
            if start < 1 or end > len(temp):
                raise ValueError("Invalid page range specified.")
            new_file.insert_pdf(temp, from_page=start - 1, to_page=end - 1)
        return __to_byte_stream(new_file)


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


def compress_pdf(file: PDF, dpi: int = 72) -> bytes:
    with fitz.open() as new_file:
        with to_PDF(file) as temp:
            for page_num in range(temp.page_count):
                page = temp.load_page(page_num)
                pix = page.get_pixmap(dpi=dpi)
                new_page = new_file.new_page(width=pix.width, height=pix.height)
                new_page.insert_image(new_page.rect, pixmap=pix)
        return __to_byte_stream(new_file)


def parse_dir(path: str) -> None:
    if not os.path.isdir(path):
        raise ValueError(f"{path} does not exist")

    docxlist = filter(lambda filename: filename.endswith(".docx"), os.listdir(path))

    docxpath = [os.path.join(path, filename) for filename in docxlist]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert(file)) for file in docxpath]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                return f"Error converting file: {e}"
    return


def merge_dir(path: str) -> bytes:
    if not os.path.isdir(path):
        raise ValueError(f"{path} does not exist")

    pdflist = filter(lambda filename: filename.endswith(".pdf"), os.listdir(path))

    pdfpaths = [os.path.join(path, filename) for filename in pdflist]

    return merge_pdfs(pdfpaths)


def find_non_pdf(args: List[str]) -> int:
    n = len(args)
    for i in range(n):
        if not args[i].endswith(".pdf"):
            return i
    return n
