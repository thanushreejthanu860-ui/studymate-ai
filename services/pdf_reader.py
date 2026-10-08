import pdfplumber


def extract_text(filepath: str) -> str:
    """Extract all text from a PDF file."""
    text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)
