# Báo Cáo Tiến Độ Dự Án

**Ngày:** 2026-01-30
**Dự án:** brsekit-test
**Kết thúc Sprint:** 2026-02-17

## ⚡ Cần hành động ngay

Các issue cần xử lý ngay:

| Issue | Summary | Type | Detail | Người thực hiện |
|-------|---------|------|--------|----------|
| BKT-3 | [BUG-INT] Nút đăng nhập không  | 🔴 Đã trễ hạn | Trễ 1 ngày | Nguyen Hoang Duong |
| BKT-7 | [ISSUE] Performance degradatio | 🔴 Lịch bất khả thi | Cần 16h nhưng chỉ 1 ngày (start=due) | bibonihongo |
| BKT-1 | [TASK] Triển khai chức năng ph | ⚠️ Cần overtime | Cần 12.0h/ngày, năng lực 6h/ngày | Nguyen Hoang Duong |
| BKT-2 | [SUBTASK] Thiết kế UI phòng ch | ⚠️ Cần overtime | Cần 8.0h/ngày, năng lực 6h/ngày | bibonihongo |
| BKT-5 | [BUG-PROD] API timeout khi loa | 📅 Sẽ trễ deadline | Hạn 02/06 → Xong 02/09 | bibonihongo |
| BKT-4 | [BUG-UAT] Hiển thị sai số tiền | 📅 Sẽ trễ deadline | Hạn 02/03 → Xong 02/04 | Nguyen Hoang Duong |
| BKT-6 | [RISK] Dependency outdated có  | 📅 Sẽ trễ deadline | Hạn 02/04 → Xong 02/06 | Nguyen Hoang Duong |

## Tổng quan

| Chỉ số | Giá trị |
|--------|-------|
| Giờ dự kiến | 172.0 |
| Giờ thực tế | 68.0 |
| Tiến độ | 39.5% |

### Theo trạng thái

| Trạng thái | Số lượng |
|--------|-------|
| Open | 4 |
| In Progress | 5 |
## BrSE Insights - Năng lực thành viên

**Ngày phân tích:** 2026-01-30 | **Năng lực:** 6h/day | **Kết thúc Sprint:** 2026-02-17

**Ghi chú:** Gap = Năng lực - Khối lượng công việc. Dương = dư, Âm = thiếu (cần điều chỉnh).

### Tổng quan năng lực

| Thành viên | Trạng thái | Task | Khối lượng | Năng lực | Gap | Tốc độ |
|--------|--------|-------|----------|----------|-----|----------|
| bibonihongo | 🟢 Đúng tiến độ | 3 | 56h | 60h | +4h | 5.6h/day |
| Nguyen Hoang Duong | ✅ Dư | 5 | 48h | 80h | +32h | 4.8h/day |

### 🟢 bibonihongo

- **Task:** 3 đang mở
- **Khối lượng:** 56h còn lại
- **Năng lực:** 60h (10 ngày × 6h/ngày)
- **Gap:** +4h (có thể hỗ trợ)
- **Phạm vi deadline:** 2026-02-03 → 2026-02-06

**Gap:** Số giờ khả dụng đến due_date trừ số giờ còn lại. Dương = còn dư thời gian, Âm = không đủ thời gian.

| Issue | Summary | DK | TT | Hạn | Gap | Cảnh báo |
|-------|---------|-----|-----|-----|-----|-------|
| BKT-2 | [SUBTASK] Thiết kế UI phò | 40h | 16h | 02/03 | -6h | 🔴 Thiếu |
| BKT-5 | [BUG-PROD] API timeout kh | 16h | 0h | 02/06 | +14h | ✅ |
| BKT-7 | [ISSUE] Performance degra | 48h | 32h | 02/03 | -10h | ⚠️ RESCHED |

### ✅ Nguyen Hoang Duong

- **Task:** 5 đang mở
- **Khối lượng:** 48h còn lại
- **Năng lực:** 80h (10 ngày × 8h/ngày)
- **Gap:** +32h (có thể hỗ trợ)
- **Phạm vi deadline:** 2026-01-29 → 2026-02-06

**Gap:** Số giờ khả dụng đến due_date trừ số giờ còn lại. Dương = còn dư thời gian, Âm = không đủ thời gian.

| Issue | Summary | DK | TT | Hạn | Gap | Cảnh báo |
|-------|---------|-----|-----|-----|-----|-------|
| BKT-3 | [BUG-INT] Nút đăng nhập k | 16h | 12h | 01/29 | -4h | 🔴 Thiếu |
| BKT-1 | [TASK] Triển khai chức nă | 16h | 4h | 01/30 | -4h | 🔴 Thiếu |
| BKT-8 | [FEEDBACK] Yêu cầu dark m | 8h | 4h | 02/06 | +44h | ✅ |
| BKT-4 | [BUG-UAT] Hiển thị sai số | 8h | 0h | 02/03 | +8h | ✅ |
| BKT-6 | [RISK] Dependency outdate | 20h | 0h | 02/04 | +4h | ✅ |

### ⚠️ Cần hành động - Task cần điều chỉnh lịch

Các task này có start_date = due_date nhưng công việc còn lại vượt năng lực/ngày.
**Không thể hoàn thành trong 1 ngày.** Vui lòng kéo dài due_date hoặc giảm scope.

| Issue | Summary | Start | Hạn | Remaining | Năng lực | Người thực hiện |
|-------|---------|-------|-----|-----------|----------|----------|
| BKT-7 | [ISSUE] Performance  | 02/03 | 02/03 | **16h** | 6h/day | bibonihongo |

### 💡 Khuyến nghị

- **⚠️ KHẨN CẤP:** 1 task có lịch bất khả thi (start=due, cần kéo dài due_date)
- **Có thể hỗ trợ:** Nguyen Hoang Duong dư +32h năng lực

## Lịch làm việc hàng ngày (Gantt) - ĐỀ XUẤT

⚠️ **Lưu ý:** Lịch dưới đây là **ĐỀ XUẤT** dựa trên năng lực thực tế. Task có due_date bất khả thi sẽ được tự động kéo dài.

### bibonihongo (6h/day)

| Task | 30F | 02M | 03T | 04W | 05T | 06F | 09M | 10T | 12T | 13F |
|------|----|----|----|----|----|----|----|----|----|----|
| **📅 BKT-2 (24h)** | 6 | 6 | 6 | 6⚠️ |  |  |  |  |  |  |
| **📅 BKT-5 (16h)** |  |  |  |  | 6 | 6 | 4⚠️ |  |  |  |
| **📅 BKT-7 (16h)** |  |  |  |  |  |  | 2 | 6 | 6 | 2⚠️ |
|------|----|----|----|----|----|----|----|----|----|----|
| **Tổng ngày** | 6h | 6h | 6h | 6h | 6h | 6h | 6h | 6h | 6h | 2h |


**Chú thích:** ✅ = đúng hạn | ⚠️ = trễ (vượt due) | ↑Xh = cần thêm X giờ | **📅 IN ĐẬM** = lịch đề xuất

### Nguyen Hoang Duong (8h/day)

| Task | 30F | 02M | 03T | 04W | 05T | 06F | 09M | 10T | 12T | 13F |
|------|----|----|----|----|----|----|----|----|----|----|
| **📅 BKT-3 (4h)** | 4⚠️ |  |  |  |  |  |  |  |  |  |
| **📅 BKT-1 (12h)** | 4 | 8⚠️ |  |  |  |  |  |  |  |  |
| BKT-8 (4h) |  |  | 4✅ |  |  |  |  |  |  |  |
| **📅 BKT-4 (8h)** |  |  | 4 | 4⚠️ |  |  |  |  |  |  |
| **📅 BKT-6 (20h)** |  |  |  | 4 | 8 | 8⚠️ |  |  |  |  |
|------|----|----|----|----|----|----|----|----|----|----|
| **Tổng ngày** | 8h | 8h | 8h | 8h | 8h | 8h |  |  |  |  |


**Chú thích:** ✅ = đúng hạn | ⚠️ = trễ (vượt due) | ↑Xh = cần thêm X giờ | **📅 IN ĐẬM** = lịch đề xuất
