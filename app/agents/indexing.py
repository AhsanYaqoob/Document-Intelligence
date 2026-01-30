from langchain_text_splitters import RecursiveCharacterTextSplitter

class IndexingAgent:
    def __init__(self):
        self.name = "IndexingAgent"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def process(self, text: str):
        """Splits text into chunks for vectorization."""
        return self.text_splitter.create_documents([text])
