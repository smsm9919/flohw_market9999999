# Flow Market – One-Click Deploy (Render)

## Quick path (Blueprint)
1. Push this repo to GitHub.
2. In Render -> New -> Blueprint -> Connect repo -> Pick this repo.
3. Render will read `render.yaml` and create:
   - Web service `flow-market`
   - PostgreSQL `flow-market-db` (free tier)
4. After first build:
   - Go to the database resource -> Copy the **Internal Connection** string -> Set it as `DATABASE_URL` env var on the web service.
   - Click **Manual Deploy -> Clear cache & deploy**.
5. Initialize tables (only if you don't use migrations yet):
   - Open **Shell** on the web service and run: `python init_db.py`

## Manual path (without blueprint)
- New -> Web Service -> Python -> Fill:
  - Build: `pip install -r requirements.txt`
  - Start: `gunicorn -c gunicorn.conf.py app:app`
- Add environment variables from `.env.production.example`.
- Add a **PostgreSQL** database in Render and set `DATABASE_URL`.
- Deploy.

## Custom domain
- Default: `https://flow-market.onrender.com`.
- Set your domain in Render -> Custom Domains (e.g. `flowmarket.site`). Add DNS CNAME to `cname.vercel-dns.com` if using a registrar, or follow Render DNS instructions.