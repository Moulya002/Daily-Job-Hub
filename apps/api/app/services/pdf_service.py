from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    extracted_pages: list[str] = []
    for page in reader.pages:
        extracted_pages.append(page.extract_text() or "")
    return "\n".join(extracted_pages).strip()


def extract_skills_from_text(text: str) -> list[str]:
    known_skills = [
        "python",
        "typescript",
        "javascript",
        "react",
        "next.js",
        "fastapi",
        "postgresql",
        "redis",
        "docker",
        "kubernetes",
        "aws",
        "gcp",
        "machine learning",
        "llm",
    ]
    normalized = text.lower()
    return [skill for skill in known_skills if skill in normalized]
