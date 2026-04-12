# Observability — query mẫu (Nhịp 3)

Postgres + bảng hiện có. Không yêu cầu dashboard riêng; Engineering có thể chạy trực tiếp trên SQL client.

## 1. Số dòng `webhook_dedupe` và độ tuổi lớn nhất

```sql
SELECT COUNT(*) AS n,
       MIN(created_at) AS oldest,
       MAX(created_at) AS newest
FROM webhook_dedupe;
```

## 2. Dedupe sẽ bị xóa bởi retention 24h (ước lượng)

```sql
SELECT COUNT(*) FROM webhook_dedupe
WHERE created_at < NOW() - INTERVAL '24 hours';
```

## 3. Funnel — token usage theo ngày (nếu có event `openai_token_usage`)

```sql
SELECT date_trunc('day', created_at) AS day,
       COUNT(*) AS events
FROM funnel_events
WHERE event_type = 'openai_token_usage'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 14;
```

## 4. Funnel — các event theo loại (7 ngày)

```sql
SELECT event_type, COUNT(*) AS n
FROM funnel_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY event_type
ORDER BY n DESC;
```

## 5. Admin audit — thao tác nhạy cảm gần đây

```sql
SELECT id, admin_user_id, action, resource_type, resource_id, created_at
FROM admin_audit_log
ORDER BY id DESC
LIMIT 50;
```

*(Đổi tên cột `created_at` nếu schema `admin_audit_log` khác — kiểm tra migration admin.)*
