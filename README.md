# Lunch-Copilot – Sprint 1 Prototype

This is a dockerized prototype for **Sprint 1** of *Amazing Lunch Indicator (ALI)*. It delivers:

- User search (free-text, type, price min/max), list results (≤100), sorting by price/name.
- Restaurant detail page.
- Minimal admin endpoints to **add restaurant types** and **add restaurants** for demo data.
- Frontend served by Nginx with an API reverse proxy under `/api/`.

## Stack
- **Frontend**: Nginx static site (HTML/JS).
- **Backend**: FastAPI + SQLAlchemy + psycopg2.
- **DB**: PostgreSQL (PostGIS image for future geo, not used yet).

## Quick start

```bash
cp .env.example .env
# (Optional) edit credentials in .env

docker compose up --build
```

App UI → http://localhost/

Healthcheck → http://localhost/api/healthz

## Seeding data via API

Create a type:

```bash
curl -X POST http://localhost/api/admin/restaurant-types   -H 'Content-Type: application/json'   -d '{"name":"Italian"}'
```

Create a restaurant:

```bash
curl -X POST http://localhost/api/admin/restaurants   -H 'Content-Type: application/json'   -d '{
    "name":"Trattoria Roma",
    "average_price":15,
    "address":"Via Example 1",
    "phone":"+34 600 000 000",
    "email":"contact@roma.example",
    "description":"Cozy Italian restaurant.",
    "type_id":1
  }'
```

Then use the UI to search and view details.

## Notes
- Tables are auto-created on backend start for prototype simplicity. Use migrations in later sprints.
- No authentication is implemented in Sprint 1.
