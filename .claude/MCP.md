# MCP (Model Context Protocol) Setup

## Configured MCP Servers

### 1. SQLite Server
Access to production database (read-only recommended for safety).

**Path**: `backend/data/database.db`

**Example queries**:
```sql
-- User statistics
SELECT COUNT(*) as total_users,
       SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users
FROM users;

-- Recent payments
SELECT p.*, u.telegram_username, p.created_at
FROM payments p
JOIN users u ON p.user_id = u.id
ORDER BY p.created_at DESC
LIMIT 10;

-- Auto-renewal status
SELECT COUNT(*) as users_with_auto_renew,
       COUNT(DISTINCT payment_method_id) as unique_payment_methods
FROM users
WHERE auto_renew_enabled = 1;
```

**Safety rules**:
- NEVER use DELETE, UPDATE, or DROP without explicit permission
- Always use SELECT for queries
- Use LIMIT to avoid large result sets

### 2. Filesystem Server
Safe file reading from the project directory.

**Useful for**:
- Reading logs without SSH
- Checking configuration files
- Analyzing code structure

### 3. GitHub Server
Integration with GitHub repository.

**Setup**: Set `GITHUB_TOKEN` environment variable with your personal access token.

**Permissions needed**:
- `repo` - full control of private repositories
- `workflow` - manage GitHub Actions workflows

**Useful for**:
- Checking CI/CD run status
- Creating issues for bugs found
- Reading PR comments
- Triggering workflows

## Installation

MCP servers are auto-installed via `npx` when Claude Code starts.

## Environment Variables

Create `.env` file in project root (if using GitHub MCP):
```
GITHUB_TOKEN=ghp_your_token_here
```

## Using MCP in Claude Code

Once configured, Claude Code automatically has access to:
- `mcp__sqlite__*` tools for database queries
- `mcp__filesystem__*` tools for file operations
- `mcp__github__*` tools for GitHub operations

## Security Notes

1. **Database access**: Local database file only. For production DB on server, use SSH + read-only queries
2. **GitHub token**: Keep it secure, don't commit to git
3. **Filesystem**: Limited to project directory only

## Recommended Workflows

### Check production DB stats:
```sql
SELECT
  COUNT(*) as total_users,
  SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_subs,
  COUNT(DISTINCT CASE WHEN auto_renew_enabled THEN payment_method_id END) as auto_renew_users
FROM users;
```

### Monitor recent payments:
```sql
SELECT status, COUNT(*) as count, SUM(amount)/100 as total_rub
FROM payments
WHERE created_at > datetime('now', '-7 days')
GROUP BY status;
```

### Check failed auto-renewals:
```sql
SELECT u.telegram_username, p.created_at, p.status
FROM payments p
JOIN users u ON p.user_id = u.id
WHERE p.is_auto_payment = 1 AND p.status = 'failed'
ORDER BY p.created_at DESC
LIMIT 20;
```
