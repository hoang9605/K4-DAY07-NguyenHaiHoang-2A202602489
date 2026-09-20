# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** [ví dụ: Customer support FAQ, Luật Việt Nam, công thức nấu ăn, ...]

**Tại sao nhóm chọn chủ đề này?**
> *Viết 2-3 câu:*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Điện thoại mới bị lỗi do nhà sản xuất được Điện Máy Chợ Lớn đổi trả trong bao lâu và có ngoại lệ nào? | Được đổi miễn phí trong vòng 35 ngày nếu lỗi do nhà sản xuất; chính sách này không áp dụng cho sản phẩm Apple. | `dien-may-cho-lon-warranty.md`, dòng 19–23 |
| 2 | Di Động Việt chờ kết quả thẩm định của hãng tối đa bao lâu tại TP.HCM và tại Tỉnh/Hà Nội; quá hạn thì xử lý thế nào? | Tối đa 15 ngày tại TP.HCM và 20 ngày tại Tỉnh/Hà Nội, tính từ ngày lập biên bản cam kết. Nếu quá thời hạn mà chưa có kết quả, Di Động Việt đổi sản phẩm dù máy có lỗi hay không. | `di-dong-viet-warranty.md`, dòng 268–272 |
| 3 | Khi khách gửi sản phẩm đến MemoryZone để bảo hành, MemoryZone chịu phần chi phí vận chuyển nào? | MemoryZone chịu chi phí một chiều để gửi trả sản phẩm đã bảo hành cho khách hàng. | `memoryzone-warranty.md`, dòng 275–289 |
| 4 | Theo tài liệu dành cho cả người mua và người bán, ai chịu trách nhiệm bảo hành sản phẩm bán trên Shopee và Shopee có trực tiếp bảo hành không? | Người bán tiếp nhận bảo hành theo chính sách của người bán hoặc nhà sản xuất. Shopee không trực tiếp chịu nghĩa vụ bảo hành và chỉ hỗ trợ trong khả năng cho phép, trừ sản phẩm do chính Shopee trực tiếp đăng bán. | `77245.md`, dòng 204–214; dùng `metadata_filter={"audience": "both"}` |
| 5 | MemoryZone có bảo hành hoặc chịu trách nhiệm đối với dữ liệu nằm trong thiết bị của khách hàng không? | Không. MemoryZone không bảo hành dữ liệu và không chịu trách nhiệm đối với dữ liệu có trong sản phẩm hoặc thiết bị khi bảo hành. | `memoryzone-warranty.md`, dòng 265–269 |

### Tự kiểm câu trả lời chuẩn

- [x] Câu 1 đối chiếu điều khoản đổi trả 35 ngày và ngoại lệ Apple trong `dien-may-cho-lon-warranty.md`.
- [x] Câu 2 đối chiếu mốc 15/20 ngày và cách xử lý quá hạn trong `di-dong-viet-warranty.md`.
- [x] Câu 3 đối chiếu quy định MemoryZone chịu phí vận chuyển một chiều gửi trả hàng trong `memoryzone-warranty.md`.
- [x] Câu 4 đối chiếu trách nhiệm của Người Bán, Nhà sản xuất và ngoại lệ sản phẩm do Shopee trực tiếp đăng bán trong `77245.md`.
- [x] Câu 5 đối chiếu tuyên bố không bảo hành và không chịu trách nhiệm về dữ liệu trong `memoryzone-warranty.md`.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

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
