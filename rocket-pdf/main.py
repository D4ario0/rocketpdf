import typer
import fitz
from pdf_model import PDF
from doc_parser import Parser

rocketpdf = typer.Typer(name="rocket-pdf")
parser = Parser


@rocketpdf.command()
def parsedoc():
    pass


@rocketpdf.command()
def parsepdf():
    pass


@rocketpdf.command()
def extract():
    pass


@rocketpdf.command()
def merge():
    pass


@rocketpdf.command()
def compress():
    pass
