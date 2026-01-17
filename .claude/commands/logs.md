# View Production Logs

Read logs from production server containers.

## Backend logs (most useful):
```bash
ssh root@89.111.131.115 "docker logs oblepiha-backend --tail 100"
```

## Frontend logs:
```bash
ssh root@89.111.131.115 "docker logs oblepiha-frontend --tail 100"
```

## Bot logs:
```bash
ssh root@89.111.131.115 "docker logs oblepiha-bot --tail 100"
```

## Follow logs in real-time:
```bash
ssh root@89.111.131.115 "docker logs oblepiha-backend -f --tail 50"
```

## Search for errors:
```bash
ssh root@89.111.131.115 "docker logs oblepiha-backend 2>&1 | grep -i error | tail -20"
```

## Tips:
- Use `--tail N` to limit output (default shows all logs)
- Use `-f` to follow logs in real-time (Ctrl+C to stop)
- Backend logs show API requests, errors, scheduler tasks
- Bot logs show Telegram bot activity
