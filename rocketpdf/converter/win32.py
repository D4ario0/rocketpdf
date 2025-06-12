from enum import IntEnum
from typing import Literal

AppType = Literal["Word.Application", "PowerPoint.Application", "Excel.Application"]
AttrType = Literal["Documents", "Presentations", "Workbooks"]


class SaveFormat(IntEnum):
    # Word formats
    WORD_TO_PDF = 17
    WORD_TO_DOCX = 16

    # Excel formats
    EXCEL_TO_PDF = 57
    EXCEL_TO_XLSX = 51

    # PowerPoint formats
    PPT_TO_PDF = 32
    PPT_TO_PPTX = 1


class WindowsConverterEngine:
    """
    WindowsConverterEngine

    This class provides a utility for converting Microsoft Office files between formats
    using the COM interface on Windows systems. It supports conversions for Word, Excel,
    and PowerPoint files into formats like PDF, DOCX, PPTX, and XLSX.

    Dependencies:
        - Requires the `comtypes` package for COM automation. Install it via `pip install comtypes`.
        - Runs only on Windows systems with the corresponding Microsoft Office applications installed.

    Methods:
        - docx_to_pdf(input_file: str, output_file: str): Converts a Word DOCX file to a PDF.
        - pdf_to_docx(input_file: str, output_file: str): Converts a PDF file to a Word DOCX.
        - pptx_to_pdf(input_file: str, output_file: str): Converts a PowerPoint PPTX file to a PDF (experimental).
        - xlsx_to_pdf(input_file: str, output_file: str): Converts an Excel XLSX file to a PDF (experimental).

    """

    def __init__(self) -> None:
        try:
            import comtypes.client

            self._app_launcher = comtypes.client.CreateObject
        except ImportError:
            raise ImportError("comtypes package required. Install with: pip install comtypes")

    def _conversion(
        self,
        input_file: str,
        output_file: str,
        app: AppType,
        attr: AttrType,
        save_format: SaveFormat,
    ) -> None:
        """
        Generic conversion function that works with different Microsoft Office applications.

        Parameters:
            input_file (str): Path to the input file.
            output_file (str): Path to the output file.
            app (AppType): The Office application to use for conversion.
            attr (AttrType): The attribute for the document type.
            save_format (SaveFormat): Format in which to save the output.
        """
        if not self._check_app_installed(app):
            raise EnvironmentError(f"{app} is not installed on this system.")

        application = None
        document = None
        try:
            application = self._app_launcher(app)
            application.visible = 1
            document = getattr(application, attr).Open(input_file)
            document.SaveAs(output_file, FileFormat=save_format.value)
        except Exception as e:
            raise RuntimeError(f"Conversion Error: {str(e)}")
        finally:
            if document:
                document.Close()
            if application:
                application.Quit()

    def docx_to_pdf(self, input_file: str, output_file: str) -> None:
        """Convert a DOCX file to PDF format."""
        return self._conversion(
            input_file=input_file,
            output_file=output_file,
            app="Word.Application",
            attr="Documents",
            save_format=SaveFormat.WORD_TO_PDF,
        )

    def pdf_to_docx(self, input_file: str, output_file: str) -> None:
        """Convert a PDF file to DOCX format."""
        return self._conversion(
            input_file=input_file,
            output_file=output_file,
            app="Word.Application",
            attr="Documents",
            save_format=SaveFormat.WORD_TO_DOCX,
        )

    def pptx_to_pdf(self, input_file: str, output_file: str) -> None:
        """Convert a PPTX file to PDF format."""
        return self._conversion(
            input_file=input_file,
            output_file=output_file,
            app="PowerPoint.Application",
            attr="Presentations",
            save_format=SaveFormat.PPT_TO_PDF,
        )

    def xlsx_to_pdf(self, input_file: str, output_file: str) -> None:
        """Convert an XLSX file to PDF format (experimental)."""
        return self._conversion(
            input_file=input_file,
            output_file=output_file,
            app="Excel.Application",
            attr="Workbooks",
            save_format=SaveFormat.EXCEL_TO_PDF,
        )

    # Helper function
    @staticmethod
    def _check_app_installed(app: AppType) -> bool:
        """
        Check if a Microsoft Office application is installed using registry.
        """

        app_exe = {
            "Word.Application": "WINWORD",
            "Excel.Application": "EXCEL",
            "PowerPoint.Application": "POWERPNT",
        }

        exe_name = app_exe.get(app)
        registry_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}.EXE"

        try:
            import winreg

            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, OSError, ImportError):
            return False
