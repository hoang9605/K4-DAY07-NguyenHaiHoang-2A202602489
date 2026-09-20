# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector biểu diễn văn bản có hướng gần nhau trong không gian embedding. Điều này thường cho thấy hai đoạn văn có nội dung hoặc ý nghĩa ngữ nghĩa gần giống nhau, ngay cả khi chúng không dùng hoàn toàn cùng từ ngữ.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Khách hàng có thể yêu cầu hoàn tiền trong vòng 7 ngày."
- Câu B: "Người mua được phép trả hàng và nhận lại tiền trong 7 ngày."
- Tại sao tương đồng: Hai câu dùng cách diễn đạt khác nhau nhưng đều nói về quyền trả hàng, hoàn tiền của người mua trong cùng thời hạn 7 ngày.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Người bán phải bảo hành sản phẩm điện tử theo chính sách."
- Câu B: "Mô hình học máy học các quy luật từ dữ liệu huấn luyện."
- Tại sao khác: Hai câu thuộc hai chủ đề và mục đích hoàn toàn khác nhau: một câu nói về chính sách bảo hành thương mại điện tử, câu còn lại nói về học máy.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào góc giữa hai vector, tức là hướng biểu diễn ngữ nghĩa, và ít bị ảnh hưởng bởi độ lớn của vector. Khoảng cách Euclid phụ thuộc cả hướng lẫn độ lớn nên có thể đánh giá hai văn bản cùng ý nghĩa là xa nhau chỉ vì độ dài hoặc chuẩn vector khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Bước trượt là `500 - 50 = 450` ký tự. Theo công thức: `ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.111...) = 23`.
>
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi `overlap=100`, bước trượt còn `500 - 100 = 400`, vì vậy số chunk là `ceil((10,000 - 100) / 400) = ceil(24.75) = 25`, tăng từ 23 lên 25 chunks. Overlap lớn hơn giúp giữ lại ngữ cảnh nằm sát ranh giới giữa hai chunk, nhưng đồng thời làm tăng dữ liệu trùng lặp, dung lượng lưu trữ và chi phí embedding/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi tách câu bằng regex nhận diện khoảng trắng hoặc xuống dòng ngay sau các dấu kết câu `.`, `!`, `?`, chẳng hạn `(?<=[.!?])(?:[ \t]+|\n+)`, rồi loại bỏ phần rỗng và chuẩn hóa khoảng trắng. Sau đó, các câu được gom tuần tự theo `max_sentences_per_chunk`; văn bản rỗng trả về danh sách rỗng, còn giá trị giới hạn nhỏ hơn 1 được chuẩn hóa thành 1. Hạn chế hiện tại là regex có thể tách sai tại chữ viết tắt như `TS.`, `v.v.` hoặc trong một số cách trình bày số thập phân.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử các separator theo thứ tự ưu tiên `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là chuỗi rỗng; mỗi cấp chia văn bản bằng separator hiện tại, ghép các phần nhỏ nếu tổng độ dài vẫn không vượt `chunk_size`, còn phần quá dài được chuyển xuống cấp separator tiếp theo. Base case là đoạn đã ngắn hơn hoặc bằng `chunk_size`; nếu hết separator hoặc separator rỗng thì cắt trực tiếp theo kích thước cố định để luôn kết thúc và vẫn xử lý được văn bản không có dấu phân cách.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` tạo embedding cho nội dung của từng `Document`, sau đó lưu bản ghi đã chuẩn hóa gồm id duy nhất, content, metadata và embedding vào bộ nhớ (hoặc collection ChromaDB nếu backend này khả dụng). `search` nhúng câu truy vấn bằng cùng một hàm embedding, tính tích vô hướng giữa vector truy vấn và từng vector tài liệu, sắp xếp điểm giảm dần rồi trả về tối đa `top_k` kết quả kèm content, metadata và score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc trước các bản ghi có metadata khớp toàn bộ cặp khóa–giá trị trong `metadata_filter`, sau đó mới tính điểm tương tự trên tập ứng viên còn lại; cách này tránh để tài liệu sai đối tượng lọt vào kết quả. `delete_document` loại bỏ tất cả bản ghi có `metadata['doc_id']` trùng với id cần xóa, so sánh kích thước trước và sau để trả về `True` nếu có bản ghi bị xóa, ngược lại trả về `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` trước hết gọi `store.search(question, top_k)` để lấy các chunk liên quan, sau đó nối nội dung các chunk thành một khối `Context` có đánh số hoặc phân cách rõ ràng. Prompt gồm chỉ dẫn yêu cầu chỉ trả lời dựa trên ngữ cảnh, phần context được truy xuất và câu hỏi của người dùng; prompt hoàn chỉnh được truyền một lần cho `llm_fn` và kết quả của mô hình được trả về dưới dạng chuỗi.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.12.5, pytest-9.1.1
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
