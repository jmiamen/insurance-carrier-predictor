"""Knowledge base document loader."""

import re
from pathlib import Path
from typing import Dict, List, Tuple

from pypdf import PdfReader

from .config import settings
from .logging_setup import logger

# Optional HTML parsing
try:
    import trafilatura

    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False
    logger.warning("trafilatura not available, HTML parsing will use basic fallback")


class DocumentChunk:
    """Represents a chunk of document text with metadata."""

    def __init__(
        self,
        text: str,
        source_path: str,
        carrier_guess: str = "",
        product_guess: str = "",
        page_num: int = None,
    ):
        """Initialize document chunk.

        Args:
            text: Chunk text content
            source_path: Path to source file
            carrier_guess: Guessed carrier name from filename/content
            product_guess: Guessed product name from filename/content
            page_num: Page number if applicable
        """
        self.text = text
        self.source_path = source_path
        self.carrier_guess = carrier_guess
        self.product_guess = product_guess
        self.page_num = page_num

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "source_path": self.source_path,
            "carrier_guess": self.carrier_guess,
            "product_guess": self.product_guess,
            "page_num": self.page_num,
        }


class KBLoader:
    """Loads and processes documents from the knowledge base."""

    def __init__(self):
        """Initialize KB loader."""
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    def load_documents(self, directory: str) -> List[DocumentChunk]:
        """Load all documents from a directory.

        Args:
            directory: Path to directory containing documents

        Returns:
            List of document chunks
        """
        path = Path(directory)
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        chunks: List[DocumentChunk] = []
        supported_extensions = {".pdf", ".html", ".htm", ".txt"}

        # Walk directory for files
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    file_chunks = self._load_file(file_path)
                    chunks.extend(file_chunks)
                    logger.info(f"Loaded {len(file_chunks)} chunks from {file_path.name}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")

        logger.info(f"Total chunks loaded: {len(chunks)} from {directory}")
        return chunks

    def _load_file(self, file_path: Path) -> List[DocumentChunk]:
        """Load a single file and return chunks.

        Args:
            file_path: Path to file

        Returns:
            List of document chunks
        """
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            text = self._extract_pdf(file_path)
        elif suffix in {".html", ".htm"}:
            text = self._extract_html(file_path)
        elif suffix == ".txt":
            text = self._extract_text(file_path)
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return []

        # Guess carrier and product from filename
        carrier_guess, product_guess = self._guess_metadata(file_path.stem, text[:500])

        # Split into chunks
        chunks = self._chunk_text(text, str(file_path), carrier_guess, product_guess)
        return chunks

    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file.

        Args:
            file_path: Path to PDF

        Returns:
            Extracted text
        """
        try:
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return ""

    def _extract_html(self, file_path: Path) -> str:
        """Extract text from HTML file.

        Args:
            file_path: Path to HTML

        Returns:
            Extracted text
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()

            if HAS_TRAFILATURA:
                # Use trafilatura for better extraction
                text = trafilatura.extract(html_content, include_comments=False)
                return text if text else ""
            else:
                # Basic HTML tag stripping
                text = re.sub(r"<[^>]+>", " ", html_content)
                text = re.sub(r"\s+", " ", text)
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting HTML {file_path}: {e}")
            return ""

    def _extract_text(self, file_path: Path) -> str:
        """Extract text from plain text file.

        Args:
            file_path: Path to text file

        Returns:
            File contents
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""

    def _guess_metadata(self, filename: str, text_sample: str) -> Tuple[str, str]:
        """Guess carrier and product from filename and text.

        Args:
            filename: Name of file (without extension)
            text_sample: First few hundred chars of text

        Returns:
            Tuple of (carrier_guess, product_guess)
        """
        # Common carrier names - must match actual carriers in system
        carriers = [
            "Mutual of Omaha",
            "Elco Mutual",
            "Kansas City Life",
            "United Home Life",
            "Transamerica",
            "Legal & General America",
            "SBLI",
            "Corebridge Financial",
        ]

        carrier_guess = ""
        product_guess = ""

        # Check filename and text for carrier names
        filename_lower = filename.lower()
        text_lower = text_sample.lower()

        for carrier in carriers:
            carrier_lower = carrier.lower()
            if carrier_lower in filename_lower or carrier_lower in text_lower:
                carrier_guess = carrier
                break

        # Try to extract product name from filename
        # Common patterns: "carrier_product.pdf", "product-brochure.pdf", etc.
        if "_" in filename:
            parts = filename.split("_")
            if len(parts) > 1:
                product_guess = parts[-1].replace("-", " ").title()
        elif "-" in filename:
            parts = filename.split("-")
            if len(parts) > 1:
                product_guess = parts[-1].replace("_", " ").title()

        return carrier_guess, product_guess

    def _chunk_text(
        self, text: str, source_path: str, carrier_guess: str, product_guess: str
    ) -> List[DocumentChunk]:
        """Split text into overlapping chunks.

        Args:
            text: Full text to chunk
            source_path: Source file path
            carrier_guess: Guessed carrier name
            product_guess: Guessed product name

        Returns:
            List of document chunks
        """
        if not text or not text.strip():
            return []

        # Simple word-based chunking
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            if chunk_text.strip():
                chunk = DocumentChunk(
                    text=chunk_text,
                    source_path=source_path,
                    carrier_guess=carrier_guess,
                    product_guess=product_guess,
                )
                chunks.append(chunk)

        return chunks


# Global loader instance
kb_loader = KBLoader()
