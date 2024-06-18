import typer
from doc_parser import *
from typing import List, Optional

rocketpdf = typer.Typer(name="rocket-pdf")


@rocketpdf.command()
def parsedoc(
    filename: str,
    args: Optional[List[str]] = typer.Argument(None),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
) -> None:
    """
    Convert a DOCX file to PDF.

    Args:
        filename (str): The path to the DOCX file.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the PDF.
    """
    try:
        file = convert_docx_pdf(filename)
        if args:
            file = __execute(args, file)
        else:
            output_filename = output or filename.replace(".docx", ".pdf")
            with to_PDF(file) as doc:
                doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error parsing document: {e}", err=True)


@rocketpdf.command()
def parsepdf(
    filename: str, output: Optional[str] = typer.Option(None, "-o", "--output")
) -> None:
    """
    Convert a PDF file to DOCX.

    Args:
        filename (str): The path to the PDF file.
        output (Optional[str]): The output filename for the DOCX.
    """
    try:
        output_path = output or filename.replace(".pdf", ".docx")
        convert_pdf_docx(filename, output_path)
    except Exception as e:
        typer.echo(f"Error parsing PDF: {e}", err=True)


@rocketpdf.command()
def extract(
    filename: str,
    start: int,
    end: Optional[int] = None,
    args: Optional[List[str]] = typer.Argument(None),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
) -> None:
    """
    Extract pages from a PDF file.

    Args:
        filename (str): The path to the PDF file.
        start (int): The starting page number.
        end (Optional[int]): The ending page number. Defaults to None.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the extracted pages.
    """
    try:
        suffix = f" - {end}" if end else ""
        if end is None:
            end = start
        file = extract_pages(filename, start, end)
        if args:
            file = __execute(args, file)
        else:
            output_filename = output or f"{filename} page(s) {start}{suffix}.pdf"
            with to_PDF(file) as doc:
                doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error extracting pages: {e}", err=True)


@rocketpdf.command()
def merge(
    pdflist: List[str], output: Optional[str] = typer.Option(None, "-o", "--output")
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
        if args:
            file = __execute(args, file)
        else:
            output_filename = output or "merged.pdf"
            with to_PDF(file) as doc:
                doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error merging PDFs: {e}", err=True)


@rocketpdf.command()
def compress(
    filename: str,
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
        file = compress_pdf(filename)
        if args:
            file = __execute(args, file)
        else:
            output_filename = output or f"{filename}-compressed.pdf"
            with to_PDF(file) as doc:
                doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error compressing PDF: {e}", err=True)


@rocketpdf.command()
def parseall(directory: str) -> None:
    """
    Convert all DOCX files in a directory to PDF.

    Args:
        directory (str): The path to the directory containing DOCX files.
    """
    try:
        parse_dir(directory)
    except Exception as e:
        typer.echo(f"Error parsing all documents in directory: {e}", err=True)


@rocketpdf.command()
def mergeall(
    directory: str,
    args: Optional[List[str]] = typer.Argument(None),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
) -> None:
    """
    Merge all PDF files in a directory into one.

    Args:
        directory (str): The path to the directory containing PDF files.
        args (Optional[List[str]]): Additional commands to execute.
        output (Optional[str]): The output filename for the merged PDF.
    """
    try:
        file = merge_dir(directory)
        if args:
            file = __execute(args, file)
        output_filename = output or "merged.pdf"
        with to_PDF(file) as doc:
            doc.save(output_filename)
    except Exception as e:
        typer.echo(f"Error merging all PDFs in directory: {e}", err=True)


# Function to chain arguments
def __execute(args: List[str], file: bytes) -> bytes:
    try:
        if args:
            next_command = args.pop(0)
            if next_command == "extract":
                start = int(args.pop(0))
                end = int(args.pop(0)) if args and args[0].isdigit() else None
                new_file = extract_pages(file, start, end)
                return __execute(args, new_file)
            elif next_command == "merge":
                sep = find_non_pdf(args)
                merge_queue = args[:sep]
                merge_queue.insert(0, file)
                new_file = merge_pdfs(merge_queue)
                return __execute(args[sep:], new_file)
            elif next_command == "compress":
                new_file = compress_pdf(file)
                return __execute(args, new_file)
            elif next_command == "parsepdf":
                convert_pdf_docx(file, "result.docx")
                return file
            else:
                typer.echo("Not a valid command", err=True)
        return file
    except Exception as e:
        typer.echo(f"Error executing command: {e}", err=True)
        return file
