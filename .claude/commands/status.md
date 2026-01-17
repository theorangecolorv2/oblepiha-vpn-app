# Check Production Status

Check the status of production services.

## Container status:
```bash
ssh root@89.111.131.115 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

## Health checks:
```bash
ssh root@89.111.131.115 "curl -s http://localhost:8000/health && echo"
ssh root@89.111.131.115 "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000"
```

## Expected output:
- `oblepiha-frontend` - Up, port 3000
- `oblepiha-backend` - Up (healthy), port 8000
- `oblepiha-bot` - Up (no ports)

## If something is wrong:
1. Check logs: `/logs`
2. DO NOT restart without user permission
3. Report the issue to the user

## Disk and memory:
```bash
ssh root@89.111.131.115 "df -h / && free -h"
```
