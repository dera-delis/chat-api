# Upstash Redis Setup for Chat API

## Your Upstash Redis Connection

Based on your Redis CLI command, here's your connection information:

### Redis URL for Environment Variable

Use this in your `REDIS_URL` environment variable:

```
rediss://default:AZDpAAIncDEzNjM5ZTkwMWU2NGE0YmM2YTNkZjEzNjQxNjdlMGYyNnAxMzcwOTc@easy-herring-37097.upstash.io:6379
```

**Important Notes:**
- Use `rediss://` (with double 's') for TLS/SSL connections
- The format is: `rediss://default:PASSWORD@HOST:PORT`

### For Northflank Deployment

1. Go to your `chat-api` service in Northflank
2. Navigate to **"Variables"** tab
3. Add or update `REDIS_URL` with:
   ```
   rediss://default:AZDpAAIncDEzNjM5ZTkwMWU2NGE0YmM2YTNkZjEzNjQxNjdlMGYyNnAxMzcwOTc@easy-herring-37097.upstash.io:6379
   ```
4. Save and redeploy

### Testing the Connection

You can test the connection using:

```bash
redis-cli --tls -u redis://default:AZDpAAIncDEzNjM5ZTkwMWU2NGE0YmM2YTNkZjEzNjQxNjdlMGYyNnAxMzcwOTc@easy-herring-37097.upstash.io:6379
```

Or test from Python:

```python
import redis

redis_url = "rediss://default:AZDpAAIncDEzNjM5ZTkwMWU2NGE0YmM2YTNkZjEzNjQxNjdlMGYyNnAxMzcwOTc@easy-herring-37097.upstash.io:6379"
r = redis.from_url(redis_url, decode_responses=True)
r.ping()  # Should return True
```

### Security Note

⚠️ **Important:** This file contains your Redis password. Don't commit it to GitHub!

The password is already in your `.gitignore`, but make sure to:
- Only use this URL in environment variables
- Never commit it to your repository
- Keep it secure in Northflank's environment variables

### Upstash Dashboard

Manage your Redis instance at: https://console.upstash.com

---

**Your Redis is ready to use!** Just add the `REDIS_URL` to your Northflank environment variables.

