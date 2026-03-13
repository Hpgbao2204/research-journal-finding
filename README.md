# Research Journal ETL (WoS + SJR)

Pipeline ETL local dùng **Python + Pandas + SQLite** để hợp nhất dữ liệu journal từ:
- `data/scimagojr 2024.csv`
- `data/wos_master_journal_list.csv`

## Output
- SQLite DB: `output/journals.db`
- Table: `Journal`
- Log file: `logs/etl_pipeline.log`

## Chạy nhanh
```bash
python3 -m pip install -r requirements.txt
python3 etl_pipeline.py
```

## Trường dữ liệu trong bảng `Journal`
- `Title`
- `ISSN`
- `SJR_Rank`
- `Subject_Area_Category`
- `Publisher`

## Ghi chú quan trọng
- Pipeline ưu tiên merge theo `ISSN`.
- Nếu file WoS không có cột ISSN, pipeline sẽ tự fallback merge theo `Title` (đã normalize), đồng thời ghi cảnh báo vào log.
- Dữ liệu thiếu (`missing`) được xử lý bằng default value để tránh lỗi khi load DB.
