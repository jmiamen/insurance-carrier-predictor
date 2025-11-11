#!/usr/bin/env python
"""CLI script to update the knowledge base index."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import embedder_service, kb_loader, logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Update knowledge base index from carrier documents"
    )
    parser.add_argument(
        "--path",
        type=str,
        default="data/carriers",
        help="Path to directory containing carrier documents (default: data/carriers)",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild even if index exists",
    )

    args = parser.parse_args()

    # Validate path
    path = Path(args.path)
    if not path.exists():
        logger.error(f"Directory not found: {args.path}")
        sys.exit(1)

    if not path.is_dir():
        logger.error(f"Path is not a directory: {args.path}")
        sys.exit(1)

    try:
        # Check if index exists
        if embedder_service.index_exists() and not args.rebuild:
            logger.info("Index already exists. Use --rebuild to force rebuild.")
            response = input("Rebuild anyway? (y/N): ")
            if response.lower() not in ["y", "yes"]:
                logger.info("Aborting.")
                sys.exit(0)

        # Load documents
        logger.info(f"Loading documents from {args.path}...")
        chunks = kb_loader.load_documents(str(path))

        if not chunks:
            logger.error("No documents found or no text extracted.")
            logger.error("Ensure directory contains .pdf, .html, or .txt files.")
            sys.exit(1)

        # Count unique files
        unique_files = set(chunk.source_path for chunk in chunks)
        logger.info(f"Loaded {len(unique_files)} files with {len(chunks)} chunks")

        # Build index
        logger.info("Building FAISS index (this may take a minute)...")
        embedder_service.build_index(chunks)

        # Save index
        logger.info("Saving index...")
        embedder_service.save_index()

        logger.info("✓ Knowledge base updated successfully!")
        logger.info(f"  Files indexed: {len(unique_files)}")
        logger.info(f"  Total chunks: {len(chunks)}")
        logger.info(f"  Index location: {embedder_service.index_dir}")

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error updating knowledge base: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
