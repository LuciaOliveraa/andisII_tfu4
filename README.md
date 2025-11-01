# Flask Recipes API — TFU 4

This repository implements a REST API for managing recipes and products using Flask + PostgreSQL, with Docker Compose for easy deployment. Code is written in **English**, follows good practices, uses transactions (ACID via SQLAlchemy), and implements the requested architecture patterns:

- **Rate limiting** (Flask-Limiter)
- **Retry** strategy (tenacity on DB/IO operations)
- **Publisher-Subscriber** (Redis pub/sub for events)
- **Cache-aside** (Redis caching for read-heavy endpoints)
- **Valet key** (short-lived JWT tokens for delegated limited access)
- **Gatekeeper** (authorization middleware enforcing permissions)
- **(Additional)**: Logging, structured project layout, Docker + docker-compose

---

## Project tree

```
flask_recipes_api/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ db.py
│  ├─ auth.py
│  ├─ cache.py
│  ├─ events.py
│  ├─ routes/
│  │  ├─ __init__.py
│  │  ├─ products.py
│  │  ├─ recipes.py
│  │  └─ valet.py
│  └─ utils.py
├─ migrations/    # created by flask-migrate (not included)
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md
```