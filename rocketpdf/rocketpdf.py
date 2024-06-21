import typer
from pathlib import Path
from typing import List, Optional
from .doc_parser import *

rocketpdf = typer.Typer(name="rocketpdf")


@rocketpdf.command()
def parsedoc(
    filename: Path,
    args: Optional[List[str]] = typer.Argument(None),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
) -> None:
    """
    Convert a DOCX file to PDF.

    Args:
        filename (Path): The path to the DOCX file.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the PDF.
    """
    try:
        file = convert_docx_pdf(filename)
        output_filename = output or filename.with_suffix(".pdf")
        file = __execute(args, file, output_filename) if args else file
        if not file:
            return
        with to_PDF(file) as doc:
            doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error parsing document")


@rocketpdf.command()
def parsepdf(
    filename: Path, output: Optional[str] = typer.Option(None, "-o", "--output")
) -> None:
    """
    Convert a PDF file to DOCX.

    Args:
        filename (Path): The path to the PDF file.
        output (Optional[str]): The output filename for the DOCX.
    """
    try:
        output_path = output or filename.with_suffix(".docx")
        convert_pdf_docx(filename, output_path)
    except Exception as e:
        typer.echo(f"Error parsing PDF")


@rocketpdf.command()
def extract(
    file_path: Path,
    start: int,
    end: Optional[int] = None,
    args: Optional[List[str]] = typer.Argument(None),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
) -> None:
    """
    Extract pages from a PDF file.

    Args:
        filename (Path): The path to the PDF file.
        start (int): The starting page number.
        end (Optional[int]): The ending page number. Defaults to None.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the extracted pages.
    """
    try:
        if args and args[0].isdigit():
            end = int(args.pop(0))
        suffix = f" - {end}" if end else ""
        end = end or start
        file = extract_pages(file_path, start, end)
        output_filename = output or f"{file_path.stem} page(s) {start}{suffix}.pdf"
        file = __execute(args, file, output_filename) if args else file
        if not file:
            return
        with to_PDF(file) as doc:
            doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error extracting pages")


@rocketpdf.command()
def merge(
    pdflist: List[Path], output: Optional[str] = typer.Option(None, "-o", "--output")
) -> None:
    """
    Merge multiple PDF files into one.

    Args:
        pdflist (List[str]): List of PDF file paths to merge.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the merged PDF.
    """
    try:
        sep = __find_non_pdf(pdflist)
        merge_queue = pdflist[:sep]
        args = pdflist[sep:]
        file = merge_pdfs(merge_queue)
        output_filename = output or "merged.pdf"
        file = __execute(args, file, output_filename) if args else file
        if not file:
            return
        with to_PDF(file) as doc:
            doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error merging PDFs")


@rocketpdf.command()
def compress(
    file_path: Path,
    args: Optional[List[str]] = typer.Argument(None),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
) -> None:
    """
    Compress a PDF file to reduce its size.

    Args:
        filename (str): The path to the PDF file.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the compressed PDF.
    """
    try:
        file = compress_pdf(file_path)
        output_filename = output or f"{file_path}-compressed.pdf"
        file = __execute(args, file, output_filename) if args else file
        if not file:
            return
        with to_PDF(file) as doc:
            doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error compressing PDF")


@rocketpdf.command()
def parsedocxs(directory: Path) -> None:
    """
    Convert all DOCX files in a directory to PDF.

    Args:
        directory (str): The path to the directory containing DOCX files.
    """
    try:
        parse_dir(directory)
    except Exception as e:
        typer.echo(f"Error parsing all documents in directory")


@rocketpdf.command()
def mergeall(
    directory: Path,
    args: Optional[List[str]] = typer.Argument(None),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
) -> None:
    """
    Merge all PDF files in a directory into one.

    Args:
        directory (Path): The path to the directory containing PDF files.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the merged PDF.
    """
    try:
        file = merge_dir(directory)
        output_filename = output or f"{directory.parent.stem}-merged.pdf"
        file = __execute(args, file, output_filename) if args else file
        if not file:
            return
        with to_PDF(file) as doc:
            doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error merging all PDFs in directory")


# Helper functions


# Function to chain arguments
def __execute(args: List[str], file: bytes, output:Path) -> bytes|None:
    try:
        if args:
            next_command = args.pop(0)
            if next_command == "extract":
                start = int(args.pop(0))
                end = int(args.pop(0)) if args and args[0].isdigit() else None
                new_file = extract_pages(file, start, end)
                return __execute(args, new_file)
            elif next_command == "merge":
                sep = __find_non_pdf(args)
                merge_queue = args[:sep]
                merge_queue.insert(0, file)
                new_file = merge_pdfs(merge_queue)
                return __execute(args[sep:], new_file)
            elif next_command == "compress":
                new_file = compress_pdf(file)
                return __execute(args, new_file)
            elif next_command == "parsepdf":
                output_path = output.suffix(".docx")
                convert_pdf_docx(file, output_path)
                return
            else:
                typer.echo(f"Not a valid command: {next_command}", err=True)
        return file
    except Exception as e:
        typer.echo(f"Error executing command: {e}", err=True)
        return file


# Function to find next argument
def __find_non_pdf(args: List[str]) -> int:
    n = len(args)
    for i in range(n):
        if not args[i].endswith(".pdf"):
            return i
    return n
