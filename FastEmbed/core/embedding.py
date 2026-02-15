from typing import Tuple
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer

from FastEmbed.config import Config


class EmbeddingEngine:
    """
    ONNX-based embedding engine.
    """

    PREFIXES = {
        "query": "task: question answering | query: ",
        "document": "title: {title} | text: ",
    }

    def __init__(
        self,
        model_id: str,
        model_dir: str,
        tokenizer_max_length: int = 512,
        providers: list[str] = ["CPUExecutionProvider"],
    ) -> None:
        """
        Initialize the EmbeddingEngine with the given model ID.

        The model will be downloaded from the Hugging Face Hub and stored
        in the local directory specified by model_dir.

        The providers list specifies the providers to use for the ONNX
        inference session. The default is ["CPUExecutionProvider"].

        Args:
            model_id (str): The ID of the model.
            model_dir (str): Local directory to store the model.
            tokenizer_max_length (int, optional):
                The maximum length of the tokenizer.
                The input will be truncated to this length.
                Defaults to 512.
            providers (list[str], optional): The list of providers to use.
                                                Defaults to ["CPUExecutionProvider"].
        """
        # Store instance variables
        self._model_id = model_id
        self._model_dir = model_dir
        self._tokenizer_max_length = tokenizer_max_length
        self._providers = providers

        # Download ONNX artifacts
        self._model_path = hf_hub_download(
            self._model_id, subfolder="onnx", filename="model.onnx"
        )
        hf_hub_download(self._model_id, subfolder="onnx", filename="model.onnx_data")

        # Create an ONNX session and tokenizer
        self._session = ort.InferenceSession(
            self._model_path, providers=self._providers
        )
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_id)

    def _embed_text(self, text: str) -> np.ndarray:
        """
        Embed a given text using the ONNX model.

        Args:
            text (str): Text to embed.

        Returns:
            np.ndarray: The embedded array of the text.
        """
        inputs = self._tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=self._tokenizer_max_length,
            return_tensors="np",
        )

        output = self._session.run(None, inputs.data)
        embedding = output[1].astype(np.float32)

        return embedding

    def serialize_embedding(self, embedding_array: np.ndarray) -> bytes:
        """
        Serialize the given embedding array into bytes.

        Args:
            embedding_array (np.ndarray): The embedding array to serialize.

        Returns:
            bytes: The serialized embedding array.
        """
        return embedding_array.astype(np.float32).tobytes()

    def deserialize_embedding(self, embedding_binary: bytes) -> np.ndarray:
        """
        Deserialize the given embedding bytes into a numpy array.

        Args:
            embedding_binary (bytes): The serialized embedding bytes.

        Returns:
            np.ndarray: The deserialized embedding array.
        """
        return np.frombuffer(embedding_binary, dtype=np.float32)

    def embed_query_text(self, query_text: str) -> np.ndarray:
        """
        Embed the given query text.

        Args:
            query_text (str): The query text to embed.

        Returns:
            np.ndarray: The embedded array of the text..
        """
        return self._embed_text(self.PREFIXES["query"] + query_text)

    def embed_document_text(
        self, document_text: str, document_title: str = "none"
    ) -> np.ndarray:
        """
        Embed the given document text.

        Args:
            document_text (str): The document text to embed.
            document_title (str, optional): The document title to use for embedding.
                Defaults to "none".

        Returns:
            np.ndarray: The embedded array of the document.
        """
        prefix = self.PREFIXES["document"].format(title=document_title)
        return self._embed_text(prefix + document_text)

    def _compute_similarity(
        self, query_embedding_array: np.ndarray, documents_embeddings_array: np.ndarray
    ) -> np.ndarray:
        """
        Compute the similarity between the query embedding and document embeddings.

        Args:
            query_embedding_array (np.ndarray): The query embedding array.
            documents_embeddings_array (np.ndarray): The documents embeddings array.

        Returns:
            np.ndarray:
            The similarity scores between the query embedding and document embeddings.
        """
        return np.dot(query_embedding_array, documents_embeddings_array.T)

    def rank_documents_by_similarity(
        self, query_embedding: np.ndarray, documents_embeddings: np.ndarray, k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Rank the documents by their similarity to the query embedding.

        Args:
            query_embedding (np.ndarray): The embedding of the query.
            documents_embeddings (np.ndarray): The embeddings of the documents.
            k (int, optional): The number of documents to rank.
                Defaults to 5.

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                The similarity scores and the indices of the ranked documents.
        """
        similarity_scores = self._compute_similarity(
            query_embedding, documents_embeddings
        )[0]

        sorted_indices = np.argsort(-similarity_scores)[:k]

        return similarity_scores[sorted_indices], sorted_indices

    def rank_documents(
        self, query_embedding: np.ndarray, documents_embeddings: np.ndarray, k: int = 5
    ):
        similarity_scores = self._compute_similarity(
            query_embedding, documents_embeddings
        )[0]
        sorted_indices = similarity_scores.argsort()[::-1][:k]

        return similarity_scores[sorted_indices], sorted_indices


embedding_engine = None


def get_embedding_engine() -> EmbeddingEngine:
    """Get the embedding engine singleton instance."""
    global embedding_engine
    if embedding_engine is None:
        embedding_engine = EmbeddingEngine(
            model_id=Config.MODEL_ID,
            model_dir=Config.MODEL_DIR,
            providers=Config.MODEL_PROVIDERS,
            tokenizer_max_length=Config.TOKENIZER_MAX_LENGTH,
        )
    return embedding_engine


def init_embedding_engine() -> EmbeddingEngine:
    return get_embedding_engine()
