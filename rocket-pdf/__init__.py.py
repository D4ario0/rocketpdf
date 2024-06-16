import typer
import os
from typing import List
from .doc_parser import Parser
from .pdf_model import PDF

rocketpdf = typer.Typer(name="rocket-pdf")
parser = Parser()


@rocketpdf.command()
def parsedoc(filename: str, args: List[str] = typer.Argument(None)):
    file = parser.convert_docx_pdf(filename)

    if args:
        file = __execute(args, file)
    else:
        file.save(filename.replace(".docx", ".pdf"))
        file.close()
        os.remove("~$temp.pdf")


@rocketpdf.command()
def parsepdf(filename: str, output: str = None):
    parser.convert_pdf_docx(
        filename, filename.replace(".pdf", ".docx" if output is None else output)
    )


@rocketpdf.command()
def extract(
    filename: str, start: int, end: int = None, args: List[str] = typer.Argument(None)
):
    suffix = f" - {end}" if end else ""

    if end is None:
        end = start

    file = parser.extract_pages(filename, start, end)

    if args:
        file = __execute(args, file)
    else:
        file.save(f"{filename} page(s) {start}{suffix}.pdf")
        file.close()


@rocketpdf.command()
def merge(pdflist: List[str]):
    sep = __find_non_pdf(pdflist)
    merge_queue = pdflist[:sep]
    args = pdflist[sep:]

    file = parser.merge_pdfs(merge_queue)

    if args:
        file = __execute(args, file)
    else:
        file.save("merged.pdf")
        file.close()


@rocketpdf.command()
def compress(filename: str, args: List[str] = typer.Argument(None)):
    file = parser.compress_pdf(filename)

    if args:
        file = __execute(args, file)
    else:
        file.save(f"{filename}-compressed")
        file.close()


@rocketpdf.command()
def parseall(directory: str):
    parser.parse_dir(directory)


@rocketpdf.command()
def mergeall(directory: str, args: List[str] = typer.Argument(None)):
    file = parser.merge_dir(directory)

    if args:
        file = __execute(args, file)

    file.save("merged.pdf")
    file.close()


# Function to chain arguments
def __execute(args: List[str], file: PDF) -> PDF:
    if args:
        next_command = args.pop(0)

        if next_command == "extract":
            start = int(args.pop(0))
            end = int(args.pop(0)) if args and args[0].isdigit() else None
            new_file = parser.extract_pages(file, start, end)
            return __execute(args, new_file)

        elif next_command == "merge":
            sep = __find_non_pdf(args)
            merge_queue = args[:sep]
            merge_queue.insert(0, file)
            new_file = parser.merge_pdfs(merge_queue)
            return __execute(args[sep:], new_file)

        elif next_command == "compress":
            new_file = parser.compress_pdf(file)
            return __execute(args, new_file)

        elif next_command == "parsepdf":
            new_file = parser.convert_pdf_docx(file, "result.docx")
            return __execute(args, new_file)

    return file


def __find_non_pdf(args: List[str]) -> int:
    for i, arg in enumerate(args):
        if ".pdf" not in arg:
            return i
    return len(args)
