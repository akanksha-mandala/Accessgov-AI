import os
import json
import logging
from typing import List, Dict, Any
from config import settings
from rag.embeddings import embedding_manager

logger = logging.getLogger("accessgov.rag.ingest")


class IngestionEngine:
    """
    Knowledge Ingestion Engine for AccessGov AI RAG Module.
    Parses JSON dataset files, chunks text metadata, and indexes vector embeddings with full metadata into ChromaDB (Refinement #3).
    """

    def __init__(self, chroma_path: str = None, dataset_path: str = None):
        self.chroma_path = chroma_path or settings.CHROMA_DB_PATH
        self.dataset_path = dataset_path or settings.KNOWLEDGE_DATA_PATH
        self._collection = None

    def _get_collection(self):
        """
        Initializes persistent ChromaDB client and gets 'accessgov_knowledge' collection.
        """
        if self._collection is None:
            try:
                import chromadb
                os.makedirs(self.chroma_path, exist_ok=True)
                client = chromadb.PersistentClient(path=self.chroma_path)
                self._collection = client.get_or_create_collection(
                    name="accessgov_knowledge",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"ChromaDB Persistent Collection connected at: {self.chroma_path}")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB collection: {str(e)}")
                self._collection = None
        return self._collection

    def load_json_files(self) -> List[Dict[str, Any]]:
        """
        Loads dataset records from JSON files in dataset_path directory.
        """
        documents = []
        if not os.path.exists(self.dataset_path):
            logger.warning(f"Dataset path {self.dataset_path} does not exist.")
            return documents

        for root, _, files in os.walk(self.dataset_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    item["_source_file"] = file
                                    documents.append(item)
                            elif isinstance(data, dict):
                                data["_source_file"] = file
                                documents.append(data)
                    except Exception as e:
                        logger.error(f"Error reading dataset file {file_path}: {str(e)}")
        return documents

    def ingest_datasets(self) -> int:
        """
        Ingests and indexes all JSON knowledge datasets into ChromaDB with enriched chunk metadata (Refinement #3).
        Metadata stored per chunk: service_name, department, source_document, language, service_code, category.
        Returns total count of indexed chunks.
        """
        records = self.load_json_files()
        if not records:
            logger.warning("No records found to ingest.")
            return 0

        collection = self._get_collection()
        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for idx, rec in enumerate(records):
            doc_id = f"doc_{idx}_{rec.get('code', rec.get('scheme_code', 'gen'))}"
            
            # Construct human-readable chunk text
            service_name = str(rec.get("title", rec.get("service_name", rec.get("scheme_name", rec.get("module", "Government Service")))))
            department = str(rec.get("department_name", rec.get("department", "Government Department")))
            source_document = str(rec.get("_source_file", "unknown_source.json"))
            language = str(rec.get("language", "en"))
            
            desc = rec.get("description", "")
            elig = rec.get("eligibility", rec.get("eligibility_criteria", ""))
            docs_req = ", ".join(rec.get("required_documents", [])) if isinstance(rec.get("required_documents"), list) else str(rec.get("required_documents_summary", ""))

            content_chunk = f"Scheme: {service_name}\nDepartment: {department}\nDescription: {desc}\nEligibility: {elig}\nRequired Documents: {docs_req}"
            
            emb = embedding_manager.embed_text(content_chunk)

            ids.append(doc_id)
            documents.append(content_chunk)
            metadatas.append({
                "service_name": service_name,
                "department": department,
                "source_document": source_document,
                "language": language,
                "service_code": str(rec.get("code", rec.get("scheme_code", ""))),
                "category": str(rec.get("category", rec.get("service_category", "General")))
            })
            embeddings.append(emb)

        if collection and ids:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            logger.info(f"Successfully indexed {len(ids)} knowledge chunks with complete metadata into ChromaDB.")
            return len(ids)

        return 0


ingestion_engine = IngestionEngine()
