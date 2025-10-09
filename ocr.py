from abc import ABC, abstractmethod


class OCRModel(ABC):
    """Abstract base class for OCR models that extract text from images."""

    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from an image file.

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Extracted text from the image
        """
        pass


class MockOCRModel(OCRModel):
    """Mock OCR model for testing and demonstration purposes."""

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image filename (mock implementation).
        Returns hardcoded strings based on filename patterns.

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Mock extracted text with typical OCR errors
        """
        filename = image_path.split("/")[-1].split("\\")[-1]

        if "test1" in filename:
            return "12 + (5 x 4) - I"
        elif "test2" in filename:
            return "3.14 * 2 + 7 / 2"
        elif "test3" in filename:
            return "8 - 4 / 2 + 1"
        elif "test4" in filename:
            return "(10 + 2) * 3 - 5"
        elif "test5" in filename:
            return "2 O + 3 l - S"
        else:
            return "1 2 + ( 5 x 4 ) - I"
