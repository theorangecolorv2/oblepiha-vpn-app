# Build and Deploy

## How deployment works

This project uses **CI/CD via GitHub Actions**. Deployment is automatic:

1. Push changes to `main` branch
2. GitHub Actions runs `.github/workflows/deploy.yml`
3. Server pulls changes and rebuilds containers

## To deploy changes:

```bash
# 1. Check code quality first
npm run lint && npm run build

# 2. Commit and push
git add . && git commit -m "Your message" && git push origin main
```

## DO NOT:
- Run `docker compose` on the production server without explicit permission
- SSH into server to modify files
- Manually restart containers

## Local testing with Docker:

For local testing only (NOT production):
```bash
docker compose up -d --build
```

## Monitor deployment:

After pushing, check server status:
```bash
ssh root@89.111.131.115 "docker ps"
ssh root@89.111.131.115 "docker logs oblepiha-backend --tail 50"
```
