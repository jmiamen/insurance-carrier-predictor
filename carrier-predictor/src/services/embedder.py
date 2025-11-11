"""Embedding and FAISS index management."""

import json
import pickle
from pathlib import Path
from typing import List, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import settings
from .kb_loader import DocumentChunk
from .logging_setup import logger


class EmbedderService:
    """Service for creating embeddings and managing FAISS index."""

    def __init__(self):
        """Initialize embedder service."""
        self.model_name = settings.embed_model_name
        self.index_dir = Path(settings.index_dir)
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.IndexFlatL2] = None
        self.metadata: List[dict] = []

        # Lazy load model
        self._load_model()

    def _load_model(self) -> None:
        """Load sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.get_dimension()}")

    def get_dimension(self) -> int:
        """Get embedding dimension.

        Returns:
            Dimension of embeddings
        """
        if self.model is None:
            self._load_model()
        return self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            self._load_model()

        logger.debug(f"Embedding {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=len(texts) > 100)
        return np.array(embeddings).astype("float32")

    def build_index(self, chunks: List[DocumentChunk]) -> None:
        """Build FAISS index from document chunks.

        Args:
            chunks: List of document chunks to index
        """
        if not chunks:
            logger.warning("No chunks provided to build index")
            return

        logger.info(f"Building index from {len(chunks)} chunks")

        # Extract texts
        texts = [chunk.text for chunk in chunks]

        # Create embeddings
        embeddings = self.embed_texts(texts)

        # Create FAISS index
        dimension = self.get_dimension()
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        # Store metadata
        self.metadata = [chunk.to_dict() for chunk in chunks]

        logger.info(f"Index built with {self.index.ntotal} vectors")

    def save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        if self.index is None:
            logger.warning("No index to save")
            return

        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = self.index_dir / "faiss.index"
        faiss.write_index(self.index, str(index_path))
        logger.info(f"Saved FAISS index to {index_path}")

        # Save metadata
        metadata_path = self.index_dir / "metadata.pkl"
        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info(f"Saved metadata to {metadata_path}")

        # Save index info
        info_path = self.index_dir / "index_info.json"
        info = {
            "num_vectors": self.index.ntotal,
            "dimension": self.get_dimension(),
            "model_name": self.model_name,
            "num_chunks": len(self.metadata),
        }
        with open(info_path, "w") as f:
            json.dump(info, f, indent=2)
        logger.info(f"Saved index info to {info_path}")

    def load_index(self) -> bool:
        """Load FAISS index and metadata from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = self.index_dir / "faiss.index"
        metadata_path = self.index_dir / "metadata.pkl"

        if not index_path.exists() or not metadata_path.exists():
            logger.warning(f"Index files not found in {self.index_dir}")
            return False

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors from {index_path}")

            # Load metadata
            with open(metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            logger.info(f"Loaded {len(self.metadata)} metadata entries from {metadata_path}")

            return True
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            self.index = None
            self.metadata = []
            return False

    def index_exists(self) -> bool:
        """Check if index files exist.

        Returns:
            True if index exists, False otherwise
        """
        index_path = self.index_dir / "faiss.index"
        metadata_path = self.index_dir / "metadata.pkl"
        return index_path.exists() and metadata_path.exists()

    def get_index_info(self) -> dict:
        """Get information about the current index.

        Returns:
            Dictionary with index information
        """
        if self.index is None:
            return {"exists": False}

        return {
            "exists": True,
            "num_vectors": self.index.ntotal,
            "dimension": self.get_dimension(),
            "num_metadata": len(self.metadata),
            "model_name": self.model_name,
        }


# Global embedder service instance
embedder_service = EmbedderService()
