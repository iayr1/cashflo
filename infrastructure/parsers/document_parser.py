import os
import PyPDF2
import docx

class DocumentParser:
    def parse(self, file_path: str) -> str:
        """
        Parses a document containing the AP Policy.
        Supports .txt, .pdf, and .docx files automatically.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Policy file not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext == '.docx':
            return self._parse_docx(file_path)
        else:
            # Fallback to text parsing
            try:
                return self._parse_text(file_path)
            except UnicodeDecodeError:
                raise ValueError(f"Unsupported binary file format: {ext}")
                
    def _parse_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
            
    def _parse_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
        
    def _parse_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
