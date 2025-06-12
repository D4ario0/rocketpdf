from pathlib import Path

from click import confirm, prompt, secho

from ..clitools import Colors, Cursors, prompter

OUT_STREAM = None


def files_with_suffix(directory: Path, ext: str) -> list[Path]:
    """
    List all files with a specific extension in a given directory.
    """

    return [f.name for f in directory.iterdir() if f.is_file() and f.suffix.lower() == ext]


def handle_in_file(ext: str) -> str:
    """
    Handle file input with support for direct file path or selection from directory.
    """
    # Prompt the user for a filename or directory path.
    target = prompt("Enter filename or directory (current dir [.])")

    path = Path(target).resolve()

    # If it is a directory.
    if path.is_dir():
        # List all files in the directory with the specified extension.
        files = files_with_suffix(path, ext)

        # If no files with the required extension are found, raise an error.
        if not files:
            raise FileNotFoundError(f"No valid files with extension {ext} found.")

        # Prompt the user to select a file from the list of valid files.
        selected_file = prompter("Select a target file: ", files)

        # If the user cancels or doesn't select a file, raise an error.
        if selected_file is None:
            raise ValueError("No file was selected")

        # Construct the full path by combining the directory and selected file.
        path = path / selected_file

    # File handling
    if path.is_file():
        # Verify that the file has the correct extension.
        if path.suffix.lower() != ext:
            raise ValueError(f"Wrong File Format. Provide a {ext} file.")

        # Check for file locks on the output file
        lock_file = path.parent / f"~${path.name[1:]}"
        if lock_file.exists():
            raise IOError(f"{path.name} is locked by another application.")

        # If all checks pass, return the absolute path as a string.
        return str(path)

    # If the path is neither a valid file nor a directory, raise an error.
    raise FileNotFoundError(f"Invalid file or directory: {target}")


def handle_out_file(output: str | None, input: str, ext: str) -> str:
    """
    Handle output file path with checks for file existence and confirmation for overwriting.
    If output is not provided, it will be constructed by replacing the input file's extension.
    """
    # Resolve the input path
    input_path = Path(input).resolve()

    # If no output path is provided, default to the input file's parent directory with a .pdf extension
    output_filename = output or input_path.stem
    output_path = (input_path.parent / output_filename).with_suffix(ext)

    # Check if the output file already exists
    if output_path.exists():
        # Ask the user if they want to overwrite the file
        confirm_overwrite = confirm(f"{output_path} already exists. Do you wish to overwrite it?")

        # If the user does not want to overwrite, abort
        if not confirm_overwrite:
            raise ValueError("Specify a different output with -o flag")

    # Check for file locks on the output file
    lock_file = output_path.parent / f"~${output_path.name[1:]}"
    if lock_file.exists():
        raise IOError(f"The output file '{output_path.name}' is locked by another application.")

    # Return the resolved output file path
    return str(output_path)


def handle_range(from_page: int, to_page: int | None, doc_length: int) -> tuple[int, int]:
    # If not to_page is given assume we are extracting a single page and match to first index
    if to_page is None:
        to_page = from_page

    if not 0 < from_page <= to_page <= doc_length:
        raise IndexError(
            f"Invalid Page Range: {from_page} to {to_page}. Min: 1 | Max: {doc_length}"
        )

    return from_page - 1, to_page - 1  # Convert to 0-based index


def page_ext_str_builder(in_filename: str, from_page: int, to_page: int | None) -> str:
    # Complex string manip. e.g. file[1-2] or file[3]
    return f"{Path(in_filename).stem}[{from_page}{f"-{to_page}" if to_page and to_page != from_page else""}]"


def log_err(e: Exception) -> None:
    secho(f"{Cursors.EXIT_CURSOR} {str(e)}", fg=Colors.RED, file=OUT_STREAM)
