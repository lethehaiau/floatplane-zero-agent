"""
Text extraction utilities for different file types.
"""
import fitz  # PyMuPDF


MAX_CHARS = 100_000  # 100K characters per file


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF using PyMuPDF.

    Args:
        file_content: PDF file content as bytes

    Returns:
        Extracted text (limited to 100K chars)

    Raises:
        Exception: If PDF extraction fails
    """
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=file_content, filetype="pdf")

        # Extract text from all pages
        text_parts = []
        total_chars = 0

        for page in doc:
            page_text = page.get_text()
            if total_chars + len(page_text) > MAX_CHARS:
                # Truncate to limit
                remaining = MAX_CHARS - total_chars
                text_parts.append(page_text[:remaining])
                break
            text_parts.append(page_text)
            total_chars += len(page_text)

        doc.close()

        return "\n".join(text_parts)

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_txt(file_content: bytes) -> str:
    """
    Extract text from TXT file.

    Args:
        file_content: TXT file content as bytes

    Returns:
        Extracted text (limited to 100K chars)

    Raises:
        Exception: If text decoding fails
    """
    try:
        # Try UTF-8 first
        text = file_content.decode("utf-8")
    except UnicodeDecodeError:
        # Fallback to latin-1
        try:
            text = file_content.decode("latin-1")
        except Exception as e:
            raise Exception(f"Failed to decode text file: {str(e)}")

    # Limit to 100K chars
    return text[:MAX_CHARS]


def extract_text_from_md(file_content: bytes) -> str:
    """
    Extract text from Markdown file.

    Args:
        file_content: MD file content as bytes

    Returns:
        Extracted text (limited to 100K chars)

    Raises:
        Exception: If text decoding fails
    """
    # Markdown is just text, same as TXT
    return extract_text_from_txt(file_content)


def extract_text(file_content: bytes, file_type: str) -> str:
    """
    Extract text from file based on type.

    Args:
        file_content: File content as bytes
        file_type: File type (pdf, txt, md)

    Returns:
        Extracted text (limited to 100K chars)

    Raises:
        ValueError: If file type is not supported
        Exception: If extraction fails
    """
    if file_type == "pdf":
        return extract_text_from_pdf(file_content)
    elif file_type == "txt":
        return extract_text_from_txt(file_content)
    elif file_type == "md":
        return extract_text_from_md(file_content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
