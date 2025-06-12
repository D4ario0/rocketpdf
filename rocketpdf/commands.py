import inspect
from typing import Optional

import click

from . import rocketpdf as rpdf
from .clitools import prompter
from .utils import io


class Extensions:
    DOCX = ".docx"
    PPTX = ".pptx"
    XLSX = ".xlsx"
    PDF = ".pdf"


FILE_ARG = click.Path(exists=True, resolve_path=True, dir_okay=False)


class Commands:
    """Contains the list of commands to execute"""

    def __init__(self, group: click.Group):
        self.commands = dict()

        for name, command in inspect.getmembers(self):
            if isinstance(command, click.Command):
                group.add_command(command)
                self.commands[name] = command

    def __description__(self) -> list[str]:
        # Find longest command name for padding
        max_name_length = max(len(cmd.name) for cmd in self.commands.values())

        # Format: "command    description"
        def format_command(cmd: click.Command) -> str:
            return f"{cmd.name:<{max_name_length}}    {cmd.callback.__doc__}"

        formatted_commands = list(map(format_command, self.commands.values()))

        return formatted_commands

    # rocketpdf commands

    @click.command()
    @click.argument(
        "in_file",
        type=FILE_ARG,
        required=False,
    )
    @click.option(
        "-o",
        "--out_file",
        type=click.Path(),
    )
    def convdocx(
        in_file: Optional[str] = None,
        out_file: Optional[str] = None,
    ):
        """Convert DOCX to PDF."""

        try:
            if not in_file:
                in_file = io.handle_in_file(Extensions.DOCX)

            out_file = io.handle_out_file(out_file, in_file, Extensions.PDF)
        except (FileNotFoundError, ValueError, IOError) as e:
            io.log_err(e)
            return

        return rpdf.docx_to_pdf(in_file, out_file)

    @click.command()
    @click.argument(
        "in_file",
        type=FILE_ARG,
        required=False,
    )
    @click.option(
        "-o",
        "--out_file",
        type=click.Path(),
    )
    def convpdf(
        in_file: Optional[str] = None,
        out_file: Optional[str] = None,
    ):
        """Convert PDF to DOCX."""

        try:
            if not in_file:
                in_file = io.handle_in_file(Extensions.PDF)

            out_file = io.handle_out_file(out_file, in_file, Extensions.DOCX)
        except (FileNotFoundError, ValueError, IOError) as e:
            io.log_err(e)
            return

        return rpdf.pdf_to_docx(in_file, out_file)

    @click.command()
    @click.argument(
        "in_file",
        type=FILE_ARG,
        required=False,
    )
    @click.argument(
        "from_page",
        type=click.IntRange(min=1),
        required=False,
    )
    @click.argument(
        "to_page",
        type=click.IntRange(min=1),
        required=False,
    )
    @click.option("-o", "--out_file", type=click.Path())
    def extract(
        in_file: Optional[str],
        from_page: Optional[int],
        to_page: Optional[int],
        out_file: Optional[str],
    ):
        """Extract Page(s) from PDF"""
        try:
            # If user enters a
            if not in_file:
                in_file = io.handle_in_file(Extensions.PDF)

            if not from_page:
                option = prompter(
                    "Would you like to extract a single page or multiple pages? ",
                    ["Single-Page", "Multi-Page"],
                )
                match option:
                    case "Single-Page":
                        from_page = int(click.prompt("Enter page number to extract"))
                    case "Multi-Page":
                        from_page = int(click.prompt("Enter initial page number"))
                        to_page = int(click.prompt("Enter final page number"))
                    case _:
                        raise ValueError("Aborted Extraction")

            # Format filename if out_file missing e.g.: Report 1-3
            if not out_file:
                out_file = io.page_ext_str_builder(in_file, from_page, to_page)

            out_file = io.handle_out_file(out_file, in_file, Extensions.PDF)
        except (FileNotFoundError, ValueError, IOError) as e:
            io.log_err(e)
            return

        return rpdf.extract_pages(in_file, from_page, to_page, out_file)

    @click.command()
    @click.argument(
        "in_file",
        type=FILE_ARG,
        required=False,
    )
    @click.option(
        "-o",
        "--out_file",
        type=click.Path(),
    )
    def compress(
        in_file: Optional[str] = None,
        out_file: Optional[str] = None,
    ):
        """Compress PDF"""

        try:
            if not in_file:
                in_file = io.handle_in_file(Extensions.PDF)

            out_file = io.handle_out_file(out_file, in_file, Extensions.PDF)
        except (FileNotFoundError, ValueError, IOError) as e:
            io.log_err(e)
            return

        return rpdf.compress_pdf(in_file, out_file, compress_img=True)

    @click.command()
    @click.argument(
        "file_list",
        type=FILE_ARG,
        required=False,
        nargs=-1,
    )
    @click.option(
        "-o",
        "--out_file",
        type=click.Path(),
    )
    def merge(file_list: tuple[str, ...], out_file: Optional[str]):
        if len(file_list) < 1:
            io.handle_in_file(Extensions.PDF)
