from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from Retrieval.rag_base import RAG

class ChromaEmbeddingsAdapter(Embeddings):
    def __init__(self, ef: EmbeddingFunction):
        self.ef = ef

    def embed_documents(self, texts):
        return self.ef(texts)

    def embed_query(self, query):
        return self.ef([query])[0]

class RAG_BASIC(RAG):
    def __init__(self):
        super().__init__()

    #Split the text
    def split(self,docs):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        splits = []
        for s in text_splitter.split_documents(docs):
            splits.append(s)
        return splits

    #Store in a vector database
    def store(self,chunks,cache):
        if cache:
            vectorstore = Chroma(persist_directory='my_dataset/vectorstore/base', embedding_function=ChromaEmbeddingsAdapter(SentenceTransformerEmbeddingFunction(model_name=self.model)))
        else:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=ChromaEmbeddingsAdapter(SentenceTransformerEmbeddingFunction(model_name=self.model,device="cuda")),
                persist_directory='my_dataset/vectorstore/base' 
                )
        return vectorstore.as_retriever(search_kwargs={"k": self.chunk_num})