from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from src.chunking import ChunkingStrategyComparator, RecursiveChunker
from src.embeddings import GeminiEmbedder
from src.models import Document
from src.store import EmbeddingStore


DATA_DIR = Path("data/warranty-policy")
CORPUS_FILES = [
    DATA_DIR / "dien-may-cho-lon-warranty.md",
    DATA_DIR / "di-dong-viet-warranty.md",
    DATA_DIR / "memoryzone-warranty.md",
    DATA_DIR / "shopee-buyer-warranty.md",
    DATA_DIR / "shopee-seller-warranty.md",
    DATA_DIR / "mediamart-h-th-ng-si-u-th-i-n-m-y-h-ng-u-vi-t-nam.md",
]

BENCHMARKS = [
    {
        "query": "Điện thoại mới bị lỗi do nhà sản xuất được Điện Máy Chợ Lớn đổi trả trong bao lâu và có ngoại lệ nào?",
        "gold": "Đổi miễn phí trong 35 ngày nếu lỗi do nhà sản xuất; không áp dụng cho sản phẩm Apple.",
        "expected_doc_id": "dien-may-cho-lon-warranty",
        "metadata_filter": None,
    },
    {
        "query": "Di Động Việt chờ thẩm định hãng tối đa bao lâu tại TP.HCM và Tỉnh/Hà Nội; quá hạn xử lý thế nào?",
        "gold": "Tối đa 15 ngày tại TP.HCM và 20 ngày tại Tỉnh/Hà Nội; quá hạn thì đổi sản phẩm dù máy có lỗi hay không.",
        "expected_doc_id": "di-dong-viet-warranty",
        "metadata_filter": None,
    },
    {
        "query": "Khi khách gửi sản phẩm đi bảo hành, bên tiếp nhận chịu chi phí vận chuyển chiều nào?",
        "gold": "Theo chính sách MemoryZone, đơn vị chịu chi phí một chiều gửi trả sản phẩm đã bảo hành cho khách hàng.",
        "expected_doc_id": "memoryzone-warranty",
        "metadata_filter": {"audience": "buyer"},
    },
    {
        "query": "Ai phải tiếp nhận yêu cầu bảo hành sản phẩm bán trên Shopee và Shopee có trực tiếp bảo hành không?",
        "gold": "Người bán tiếp nhận bảo hành theo chính sách của người bán hoặc nhà sản xuất; Shopee chỉ hỗ trợ và không trực tiếp bảo hành, trừ sản phẩm do Shopee đăng bán.",
        "expected_doc_id": "shopee-seller-warranty",
        "metadata_filter": {"audience": "seller"},
    },
    {
        "query": "MemoryZone có bảo hành hoặc chịu trách nhiệm đối với dữ liệu trong thiết bị của khách hàng không?",
        "gold": "Không; MemoryZone không bảo hành và không chịu trách nhiệm đối với dữ liệu trong thiết bị khi bảo hành.",
        "expected_doc_id": "memoryzone-warranty",
        "metadata_filter": None,
    },
]


class HeadingChunker:
    """Split policy documents by structural headings, then recursively by size."""

    HEADING_RE = re.compile(
        r"(?m)^(?:#{1,6}\s+.+|(?:[IVXLCDM]+|[A-Z])\.\s+\S.*)$"
    )

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []

        matches = list(self.HEADING_RE.finditer(text))
        if not matches:
            return RecursiveChunker(chunk_size=self.chunk_size).chunk(text)

        chunks: list[str] = []
        prefix = text[: matches[0].start()].strip()
        if prefix:
            chunks.extend(RecursiveChunker(chunk_size=self.chunk_size).chunk(prefix))

        for index, match in enumerate(matches):
            section_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            heading = match.group(0).strip()
            body = text[match.end() : section_end].strip()
            section = f"{heading}\n{body}".strip()
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            available_size = self.chunk_size - len(heading) - 1
            if available_size <= 0:
                chunks.extend(RecursiveChunker(chunk_size=self.chunk_size).chunk(section))
                continue

            body_chunks = RecursiveChunker(chunk_size=available_size).chunk(body)
            chunks.extend(f"{heading}\n{part}".strip() for part in body_chunks)

        return chunks


class CachedNormalizedEmbedder:
    """Cache normalized embeddings by content hash for repeatable API runs."""

    def __init__(self, embedding_fn, cache_dir: Path = Path(".cache/gemini_embeddings")) -> None:
        self.embedding_fn = embedding_fn
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._backend_name = getattr(embedding_fn, "_backend_name", embedding_fn.__class__.__name__)

    def _cache_path(self, text: str) -> Path:
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key}.json"

    @staticmethod
    def _normalize(vector) -> list[float]:
        values = [float(value) for value in vector]
        magnitude = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / magnitude for value in values]

    def _store(self, text: str, vector) -> list[float]:
        normalized = self._normalize(vector)
        self._cache_path(text).write_text(json.dumps(normalized), encoding="utf-8")
        return normalized

    def preload(self, texts: list[str], batch_size: int = 50) -> None:
        missing = list(dict.fromkeys(text for text in texts if not self._cache_path(text).is_file()))
        for start in range(0, len(missing), batch_size):
            batch = missing[start : start + batch_size]
            for attempt in range(3):
                try:
                    response = self.embedding_fn.client.models.embed_content(
                        model=self.embedding_fn.model_name,
                        contents=batch,
                    )
                    break
                except Exception as error:
                    if getattr(error, "status_code", None) != 429 or attempt == 2:
                        raise
                    print("Gemini đạt giới hạn theo phút; chờ 60 giây rồi thử lại...", flush=True)
                    time.sleep(60)
            for text, embedding in zip(batch, response.embeddings):
                self._store(text, embedding.values)
            print(f"Đã cache {min(start + len(batch), len(missing))}/{len(missing)} embeddings còn thiếu", flush=True)

    def __call__(self, text: str) -> list[float]:
        cache_path = self._cache_path(text)
        if cache_path.is_file():
            return [float(value) for value in json.loads(cache_path.read_text(encoding="utf-8"))]

        return self._store(text, self.embedding_fn(text))


# Mỗi thành viên chỉ đổi dòng này để thử một chiến lược riêng.
CHUNKER = HeadingChunker(chunk_size=500)


def parse_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"{path} không có YAML frontmatter hợp lệ")

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, parts[2].strip()


def build_documents(chunker=CHUNKER) -> list[Document]:
    documents: list[Document] = []
    for path in CORPUS_FILES:
        frontmatter, content = parse_markdown(path)
        for index, chunk in enumerate(chunker.chunk(content)):
            metadata = {
                **frontmatter,
                "doc_id": path.stem,
                "file_path": str(path),
                "chunk_index": index,
            }
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata=metadata,
                )
            )
    return documents


def baseline_rows(paths: list[Path] | None = None, chunk_size: int = 500) -> list[dict]:
    selected_paths = paths or CORPUS_FILES[:3]
    comparator = ChunkingStrategyComparator()
    rows: list[dict] = []
    for path in selected_paths:
        _, content = parse_markdown(path)
        comparison = comparator.compare(content, chunk_size=chunk_size)
        for strategy, stats in comparison.items():
            rows.append(
                {
                    "document": path.stem,
                    "strategy": strategy,
                    "count": stats["count"],
                    "avg_length": stats["avg_length"],
                }
            )
    return rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    missing = [str(path) for path in CORPUS_FILES if not path.is_file()]
    if missing:
        print("Thiếu file corpus:")
        for path in missing:
            print(f"- {path}")
        return 1

    load_dotenv(dotenv_path=Path(".env"), override=False)
    print("Đang kết nối Gemini embedding...")
    embedder = CachedNormalizedEmbedder(GeminiEmbedder())
    documents = build_documents()
    embedder.preload(
        [document.content for document in documents]
        + [benchmark["query"] for benchmark in BENCHMARKS]
    )
    store = EmbeddingStore("warranty_benchmark", embedding_fn=embedder)
    store.add_documents(documents)

    print(f"Chiến lược: {CHUNKER.__class__.__name__}")
    print(f"Đã nạp: {store.get_collection_size()} chunks từ {len(CORPUS_FILES)} tài liệu")

    hits = 0
    for number, benchmark in enumerate(BENCHMARKS, start=1):
        results = store.search_with_filter(
            benchmark["query"],
            top_k=3,
            metadata_filter=benchmark["metadata_filter"],
        )
        hit = any(
            result["metadata"]["doc_id"] == benchmark["expected_doc_id"]
            for result in results
        )
        hits += int(hit)

        print(f"\n{'=' * 80}")
        print(f"Câu {number}: {benchmark['query']}")
        print(f"Gold: {benchmark['gold']}")
        print(f"Filter: {benchmark['metadata_filter']}")
        print(f"Relevant source in top-3: {'YES' if hit else 'NO'}")
        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]
            preview = " ".join(result["content"].split())[:280]
            print(
                f"Top-{rank}: score={result['score']:.4f} "
                f"doc_id={metadata['doc_id']} chunk={metadata['chunk_index']}"
            )
            print(f"  {preview}")

    print(f"\nHIT@3: {hits}/{len(BENCHMARKS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
