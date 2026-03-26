from typing import List
from core.entities.rule import Rule
from infrastructure.llm.llm_client import LLMClient
from infrastructure.parsers.document_parser import DocumentParser

class ExtractRulesUseCase:
    def __init__(self, llm_client: LLMClient, document_parser: DocumentParser):
        self.llm_client = llm_client
        self.document_parser = document_parser

    def execute(self, file_path: str) -> List[Rule]:
        text = self.document_parser.parse(file_path)
        return self.llm_client.extract_rules(text)
