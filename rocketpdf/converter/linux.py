import subprocess
from shutil import which
from typing import Literal

FILE_EXT = Literal["pdf", "docx", "pptx", "xlsx"]


class LinuxConverterEngine:
    def __init__(self):
        if not self._is_soffice_installed():
            raise EnvironmentError("LibreOffice (soffice) is not installed on this system.")

    def _convert(self, input_file: str, output_file: str, target_format: FILE_EXT) -> None:
        """Generic conversion function using soffice."""
        try:
            subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    target_format,
                    "--outdir",
                    output_file.rsplit("/", 1)[0],
                    input_file,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Conversion failed: {e}")

    def docx_to_pdf(self, input_file: str, output_file: str) -> None:
        """Convert DOCX to PDF."""
        self._convert(input_file, output_file, "pdf")

    def pdf_to_docx(self, input_file: str, output_file: str) -> None:
        """Convert PDF to DOCX (requires LibreOffice)."""
        self._convert(input_file, output_file, "docx")

    def pptx_to_pdf(self, input_file: str, output_file: str) -> None:
        """Convert PPTX to PDF."""
        self._convert(input_file, output_file, "pdf")

    def xlsx_to_pdf(self, input_file: str, output_file: str) -> None:
        """Convert XLSX to PDF."""
        self._convert(input_file, output_file, "pdf")

    # Helper functions
    @staticmethod
    def _is_soffice_installed() -> bool:
        """Check if soffice (LibreOffice) is installed."""
        return which("soffice")
