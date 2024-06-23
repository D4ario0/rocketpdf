import typer
from pathlib import Path
from typing import Optional, List
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
        file = execute(args, file, output_filename) if args else file
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
        file = execute(args, file, output_filename) if args else file
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
        sep = find_non_pdf(pdflist)
        merge_queue = pdflist[:sep]
        args = pdflist[sep:]
        file = merge_pdfs(merge_queue)
        output_filename = output or "merged.pdf"
        file = execute(args, file, output_filename) if args else file
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
        file = execute(args, file, output_filename) if args else file
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
        file = execute(args, file, output_filename) if args else file
        if not file:
            return
        with to_PDF(file) as doc:
            doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error merging all PDFs in directory")
