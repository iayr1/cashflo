class DocumentParser:
    def parse(self, file_path: str) -> str:
        """
        Reads the document and returns its text content.
        In a production system, this could handle PDF, DOCX, etc.
        For simplicity, it reads raw text.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
