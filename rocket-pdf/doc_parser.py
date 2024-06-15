import os
import fitz
from platform import system
from pdf_model import PDF


class Parser:
    def __init__(self):
        self.os = system()
        if self.os in ["Windows", "Darwin"]:
            from docx2pdf import convert
            from pdf2docx import Converter

            self.docx_to_pdf = convert
            self.pdf_to_docx = Converter
        else:
            import uno

            self.uno = uno

    def convert_docx_pdf(self, file_path: str) -> fitz.Document:
        if self.os in ["Windows", "Darwin"]:
            temp_pdf_path = "temp.pdf"
            self.docx_to_pdf(file_path, temp_pdf_path)
            file = fitz.open(temp_pdf_path)
            os.remove(temp_pdf_path)
            return file
        else:
            raise NotImplementedError("Conversion not implemented for this OS.")

    def convert_pdf_docx(self, file: PDF, docx_path: str):
        if self.os in ["Windows", "Darwin"]:
            converter = self.pdf_to_docx(file.source)
            if not docx_path.endswith(".docx"):
                docx_path += ".docx"

            converter.convert(docx_path)
            converter.close()
        else:
            raise NotImplementedError("Conversion not implemented for this OS.")

    def merge_pdfs(self, pdf_list: list[PDF]) -> fitz.Document:
        new_file = fitz.open()
        for pdf in pdf_list:
            new_file.insert_pdf(self.toPDF(pdf))
        return new_file

    def extract_pages(self, file: PDF, start: int, end: int) -> fitz.Document:
        new_file = fitz.open()
        temp = self.toPDF(file)
        if start < 1 or end > len(temp):
            raise ValueError("Invalid page range specified.")
        new_file.insert_pdf(temp, from_page=start - 1, to_page=end - 1)
        return new_file

    def convert_pdf_txt(self, file: PDF):
        content = ""
        doc = self.toPDF(file)
        for page in doc:
            output = page.get_text("blocks")
            previous_block_id = 0
            for block in output:
                if block[6] == 0:
                    if previous_block_id != block[5]:
                        content += "\n"
                    content += block[4]
        return content

    @staticmethod
    def toPDF(file: PDF):
        return file if file.is_doc else fitz.open(file)
