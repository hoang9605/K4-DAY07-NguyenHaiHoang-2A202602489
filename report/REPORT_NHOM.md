# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Trike
**Thành viên:** Nguyễn Hải Hoàng, Hoàng Văn Nam, Lê Tuấn Đạt
**Ngày:** 20/9/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách bảo hành sản phẩm tại các nhà bán lẻ và sàn thương mại điện tử ở Việt Nam

**Tại sao nhóm chọn chủ đề này?**
> Chính sách bảo hành chứa nhiều điều kiện, mốc thời gian, ngoại lệ và quy trình khác nhau giữa từng đơn vị, nên phù hợp để đánh giá khả năng truy xuất thông tin chính xác của hệ thống RAG. Chủ đề này cũng có nhiều nguồn công khai bằng tiếng Việt và cho phép kiểm tra vai trò của metadata khi cùng một vấn đề có nội dung dành riêng cho người mua và người bán.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách bảo hành 24hStore | <https://24hstore.vn/> | 20/09/2026 / không nêu | 70.567 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 2 | Chính sách bảo hành An Phát PC | <https://www.anphatpc.com.vn/> | 20/09/2026 / không nêu | 1.846 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 3 | Chính sách bảo hành và đổi trả CellphoneS | <https://cellphones.com.vn/chinh-sach-bao-hanh> | 20/09/2026 / không nêu | 3.704 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 4 | Chính sách bảo hành Di Động Việt | <https://didongviet.vn/chinh-sach-bao-hanh-dien-thoai.html> | 20/09/2026 / không nêu | 16.525 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 5 | Chính sách bảo hành Điện Máy Chợ Lớn | <https://dienmaycholon.com/chinh-sach-bao-hanh> | 20/09/2026 / không nêu | 1.794 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 6 | Chính sách bảo hành MediaMart | <https://baohanh.mediamart.vn> | 20/09/2026 / không nêu | 1.712 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 7 | Chính sách bảo hành MemoryZone | <https://memoryzone.com.vn/pages/chinh-sach-bao-hanh> | 20/09/2026 / không nêu | 14.392 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 8 | Quyền và điều kiện bảo hành dành cho Người Mua trên Shopee | <https://help.shopee.vn/portal/4/article/77245> | 20/09/2026 / không nêu | 965 | `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 9 | Trách nhiệm bảo hành của Người Bán trên Shopee | <https://help.shopee.vn/portal/4/article/77245> | 20/09/2026 / không nêu | 730 | `audience=seller`, `category=warranty-policy`, `language=vi` |
| 10 | Chính sách bảo hành XTmobile | <https://www.xtmobile.vn/chinh-sach-bao-hanh> | 20/09/2026 / không nêu | 43.160 | `audience=buyer`, `category=warranty-policy`, `language=vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `memoryzone-warranty` | Liên kết mọi chunk về đúng tài liệu gốc và hỗ trợ xóa toàn bộ chunk của một tài liệu. |
| `title` | `str` | `Chính sách bảo hành MemoryZone` | Hiển thị tên nguồn dễ hiểu khi đối chiếu kết quả truy xuất. |
| `source_url` | `str` | `https://memoryzone.com.vn/pages/chinh-sach-bao-hanh` | Truy vết câu trả lời về trang công khai ban đầu. |
| `retrieved_at` | `date` dạng `YYYY-MM-DD` | `2026-09-20` | Đánh giá độ mới của dữ liệu và biết thời điểm cần crawl lại. |
| `document_version` | `str` | `not-stated` | Phân biệt phiên bản hoặc ngày hiệu lực khi nguồn có công bố. |
| `audience` | `enum` | `buyer`, `seller` | Lọc trước theo đúng đối tượng, tránh trộn chính sách dành cho người mua và người bán. |
| `category` | `str` | `warranty-policy` | Giới hạn truy xuất theo loại tài liệu khi corpus được mở rộng. |
| `language` | mã ngôn ngữ | `vi` | Chọn tài liệu cùng ngôn ngữ với truy vấn hoặc mô hình embedding phù hợp. |
| `license_or_permission` | `str` | `public-source` | Ghi nhận cơ sở sử dụng và hỗ trợ kiểm tra quản trị dữ liệu. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Điện Máy Chợ Lớn | FixedSizeChunker (`fixed_size`) | 4 | 433.00 | Thấp — có thể cắt giữa điều kiện và ngoại lệ |
| Điện Máy Chợ Lớn | SentenceChunker (`by_sentences`) | 2 | 864.50 | Cao theo câu, nhưng chunk vượt xa ngưỡng 500 ký tự |
| Điện Máy Chợ Lớn | RecursiveChunker (`recursive`) | 4 | 428.75 | Khá — ưu tiên ranh giới đoạn/câu |
| Di Động Việt | FixedSizeChunker (`fixed_size`) | 33 | 489.18 | Trung bình — kích thước đều nhưng cắt theo ký tự |
| Di Động Việt | SentenceChunker (`by_sentences`) | 45 | 356.42 | Khá — giữ câu trọn vẹn nhưng độ dài không đều |
| Di Động Việt | RecursiveChunker (`recursive`) | 38 | 421.34 | Tốt — cân bằng kích thước và ranh giới ngữ nghĩa |
| MemoryZone | FixedSizeChunker (`fixed_size`) | 29 | 482.93 | Trung bình — có thể tách rời tiêu đề và nội dung |
| MemoryZone | SentenceChunker (`by_sentences`) | 30 | 464.23 | Khá — giữ câu nhưng đôi lúc gom các mục khác nhau |
| MemoryZone | RecursiveChunker (`recursive`) | 34 | 409.21 | Tốt — giữ đoạn/mục tốt hơn trong giới hạn kích thước |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Hải Hoàng**
- **Loại chiến lược:** Custom `HeadingChunker` + fallback `RecursiveChunker`
- **Mô tả & lý do chọn cho chủ đề này:** Chính sách bảo hành thường được tổ chức theo mục Markdown, số La Mã hoặc chữ cái, nên tiêu đề là ranh giới ngữ nghĩa tự nhiên. Mỗi section được giữ nguyên nếu đủ ngắn; section quá dài được chia đệ quy và tiêu đề được gắn lại vào từng chunk con để không mất chủ đề.
- **Code snippet (nếu custom):**
```python
# Mỗi thành viên chỉ thay dòng chọn chiến lược để so sánh công bằng.
CHUNKER = HeadingChunker(chunk_size=500)
```

**Thành viên 2 — Lê Tuấn Đạt (2A202602623)**
- **Loại chiến lược:** Custom `SlidingSentenceChunker(3, 1)` — cửa sổ trượt theo câu có chồng lấn. Chiến lược này khác nguyên lý với cách chia theo heading của thành viên 1, tạo hai hướng đối lập để so sánh.
- **Mô tả & lý do chọn:** Văn bản được chia thành cửa sổ nhỏ gồm 3 câu và mỗi chunk dùng chung 1 câu với chunk kế tiếp. Chồng lấn giúp giữ dữ kiện nằm sát ranh giới, đổi lại số chunk tăng và mỗi chunk có ít ngữ cảnh bao quanh hơn.
- **Code snippet (nếu custom):**
```python
CHUNKER = SlidingSentenceChunker(3, 1)
```

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Hải Hoàng | Custom `HeadingChunker` + fallback `RecursiveChunker` | **5/10** (chunk-level, lần chạy so sánh chung) | Giữ tiêu đề và ngữ cảnh của điều khoản; thắng Q1 vì giữ điều kiện 35 ngày cùng ngoại lệ Apple | Phụ thuộc cấu trúc heading; Q4 và Q5 có đúng tài liệu nhưng gold chunk nằm ngoài top-3 |
| Lê Tuấn Đạt | Custom `SlidingSentenceChunker(3, 1)` — cửa sổ trượt có chồng lấn | **7/10** (chunk-level), **8/10** (doc-level) | Khoanh đúng dữ kiện cụ thể: Q5 hạng 1 và Q4 hạng 3; overlap hạn chế mất dữ kiện ở ranh giới | Chunk trung bình chỉ 192 ký tự nên dễ mất ngữ cảnh; Q1 tách bullet khỏi dòng “Lưu ý”; số chunk gấp 2,9 lần nên tốn bộ nhớ và thời gian embedding |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Trên lần chạy so sánh chung, `SlidingSentenceChunker` tốt hơn về tổng điểm chunk-level (7/10 so với 5/10) vì cửa sổ nhỏ định vị chính xác các dữ kiện ngắn ở Q4 và Q5. Tuy nhiên, `HeadingChunker` tốt hơn ở Q1 vì giữ điều kiện và ngoại lệ trong cùng một mục. Vì vậy không có chiến lược thắng tuyệt đối: sliding phù hợp tra cứu dữ kiện cụ thể, còn heading phù hợp điều khoản cần ngữ cảnh trọn vẹn.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Điện thoại mới bị lỗi do nhà sản xuất được Điện Máy Chợ Lớn đổi trả trong bao lâu và có ngoại lệ nào? | Được đổi miễn phí trong vòng 35 ngày nếu lỗi do nhà sản xuất; chính sách này không áp dụng cho sản phẩm Apple. | `dien-may-cho-lon-warranty.md`, dòng 21 |
| 2 | Di Động Việt chờ kết quả thẩm định của hãng tối đa bao lâu tại TP.HCM và tại Tỉnh/Hà Nội; quá hạn thì xử lý thế nào? | Tối đa 15 ngày tại TP.HCM và 20 ngày tại Tỉnh/Hà Nội, tính từ ngày lập biên bản cam kết. Nếu quá thời hạn mà chưa có kết quả, Di Động Việt đổi sản phẩm dù máy có lỗi hay không. | `di-dong-viet-warranty.md`, dòng 272 |
| 3 | Khi khách gửi sản phẩm đi bảo hành, bên tiếp nhận chịu chi phí vận chuyển chiều nào? | Theo chính sách MemoryZone, đơn vị chịu chi phí một chiều để gửi trả sản phẩm đã bảo hành cho khách hàng. | `memoryzone-warranty.md`, dòng 289; dùng `metadata_filter={"audience": "buyer"}` |
| 4 | Ai phải tiếp nhận yêu cầu bảo hành sản phẩm bán trên Shopee và Shopee có trực tiếp bảo hành không? | Người bán tiếp nhận bảo hành theo chính sách của người bán hoặc nhà sản xuất. Shopee không trực tiếp chịu nghĩa vụ bảo hành và chỉ hỗ trợ trong khả năng cho phép, trừ sản phẩm do chính Shopee trực tiếp đăng bán. | `shopee-seller-warranty.md`, dòng 14–22; dùng `metadata_filter={"audience": "seller"}` |
| 5 | MemoryZone có bảo hành hoặc chịu trách nhiệm đối với dữ liệu nằm trong thiết bị của khách hàng không? | Không. MemoryZone không bảo hành dữ liệu và không chịu trách nhiệm đối với dữ liệu có trong sản phẩm hoặc thiết bị khi bảo hành. | `memoryzone-warranty.md`, dòng 267 |

### Tự kiểm câu trả lời chuẩn

- [x] Câu 1 đối chiếu điều khoản đổi trả 35 ngày và ngoại lệ Apple trong `dien-may-cho-lon-warranty.md`.
- [x] Câu 2 đối chiếu mốc 15/20 ngày và cách xử lý quá hạn trong `di-dong-viet-warranty.md`.
- [x] Câu 3 đối chiếu quy định MemoryZone chịu phí vận chuyển một chiều gửi trả hàng trong `memoryzone-warranty.md`; query dùng bộ lọc `audience=buyer`.
- [x] Câu 4 đối chiếu trách nhiệm của Người Bán, vai trò của Shopee và ngoại lệ sản phẩm do Shopee trực tiếp đăng bán trong `shopee-seller-warranty.md`; query dùng bộ lọc `audience=seller`.
- [x] Câu 5 đối chiếu tuyên bố không bảo hành và không chịu trách nhiệm về dữ liệu trong `memoryzone-warranty.md`.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).
>
> Bảng dưới dùng lần chạy so sánh chung của hai thành viên trên cùng điều kiện. Kết quả này khác lần chạy độc lập của `bench.py` trong báo cáo cá nhân vì lần chạy chung chấm đúng thứ hạng của chunk chứa gold answer trên corpus so sánh.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Chunk chứa gold answer nằm ở đâu? | Hoàng | Đạt |
|---|---|---|---|---:|---:|
| 1 | Chợ Lớn: 35 ngày và ngoại lệ Apple | **Heading** | Hoàng: hạng 3; Đạt: ngoài top-3 | **1** | 0 |
| 2 | Di Động Việt: thời hạn 15/20 ngày | Hòa | Cả hai: **hạng 1** | 2 | 2 |
| 3 | MemoryZone: chi phí vận chuyển một chiều | Hòa | Cả hai: **hạng 1** | 2 | 2 |
| 4 | Shopee: bên chịu trách nhiệm bảo hành | **Sliding** | Hoàng: hạng 4/137; Đạt: hạng 3 | 0 | **1** |
| 5 | MemoryZone: trách nhiệm đối với dữ liệu | **Sliding** | Hoàng: hạng 30/200; Đạt: **hạng 1** | 0 | **2** |
|  |  |  | **Tổng** | **5/10** | **7/10** |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, rõ nhất ở câu 4 vì corpus có hai tài liệu Shopee dùng từ vựng gần giống nhau nhưng dành cho hai đối tượng khác nhau. `metadata_filter={"audience": "seller"}` loại nội dung buyer khỏi tập ứng viên trước khi xếp hạng, giúp ngữ cảnh nhất quán với trách nhiệm của Người Bán. Tuy vậy, kết quả so sánh cũng cho thấy metadata đúng chưa đủ: chiến lược chunking vẫn quyết định gold answer có lọt vào top-3 hay không.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
