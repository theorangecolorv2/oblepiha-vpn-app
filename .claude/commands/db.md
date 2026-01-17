# Database Queries

Quick database statistics and queries (read-only).

**IMPORTANT**: This accesses LOCAL database file at `backend/data/database.db`.
For PRODUCTION queries, use SSH to copy the DB first or query via API.

## User Statistics

Total users and active subscriptions:
```sql
SELECT
  COUNT(*) as total_users,
  SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_subscriptions,
  SUM(CASE WHEN auto_renew_enabled = 1 THEN 1 ELSE 0 END) as auto_renew_enabled,
  SUM(CASE WHEN trial_used = 1 THEN 1 ELSE 0 END) as trial_users
FROM users;
```

## Payment Statistics

Last 7 days:
```sql
SELECT
  status,
  COUNT(*) as count,
  SUM(amount)/100.0 as total_rub
FROM payments
WHERE created_at > datetime('now', '-7 days')
GROUP BY status
ORDER BY count DESC;
```

## Recent Activity

Last 10 payments:
```sql
SELECT
  p.id,
  u.telegram_username,
  p.amount/100.0 as amount_rub,
  p.status,
  p.is_auto_payment,
  datetime(p.created_at) as created
FROM payments p
LEFT JOIN users u ON p.user_id = u.id
ORDER BY p.created_at DESC
LIMIT 10;
```

## Auto-Renewal Issues

Failed auto-payments:
```sql
SELECT
  u.telegram_username,
  u.telegram_id,
  datetime(p.created_at) as failed_at,
  p.amount/100.0 as amount_rub
FROM payments p
JOIN users u ON p.user_id = u.id
WHERE p.is_auto_payment = 1 AND p.status = 'failed'
ORDER BY p.created_at DESC
LIMIT 20;
```

## SAFETY RULES:
- ALWAYS use SELECT (read-only)
- NEVER use DELETE, UPDATE, DROP without explicit permission
- Use LIMIT to avoid large results
- For production DB: copy to local first via SSH

## Accessing Production DB:

```bash
# Copy production DB to local for analysis
ssh root@89.111.131.115 "cat /opt/oblepiha-vpn-app/backend/data/database.db" > backend/data/database-prod.db

# Then update mcp.json to point to database-prod.db temporarily
```
