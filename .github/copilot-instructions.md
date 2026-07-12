# Copilot Instructions for this repository

## Build, run, test, and lint commands

| Purpose | Command | Notes |
| --- | --- | --- |
| Install dependencies | `pip install -r requirements.txt` | Uses the root `requirements.txt`. |
| Run application | `python run.py` | Starts Flask via `create_app()` with `debug=True`. |
| Automated tests | _Not configured in this repo_ | No `tests/` directory or pytest/unittest config found. |
| Single test execution | _Not configured in this repo_ | Add a test framework before relying on per-test commands. |
| Lint/type-check | _Not configured in this repo_ | No lint or type-check config files were found. |

## High-level architecture

- This is a Flask + SQLAlchemy backend organized with an app-factory entrypoint:
  - `run.py` imports `create_app()` from `app/__init__.py`.
  - `app/__init__.py` initializes a global `db = SQLAlchemy()` and registers blueprints.
- Current HTTP surface is focused on clients:
  - `app/routes/clientes_routes.py` exposes CRUD endpoints under `/api/clientes`.
  - Routes are thin controllers that validate request payload shape and map service outcomes to HTTP codes.
- Business/data access logic lives in a service layer:
  - `app/services/cliente_service.py` performs ORM reads/writes and commits.
  - It also uses targeted raw SQL (`sqlalchemy.text`) for cross-table checks (`facturas` existence) before delete.
- Data model is centered on `Cliente` (`app/models/cliente.py`) with string primary keys and business-specific fields.
- Database evolution is tracked with SQL scripts in `.sql/`:
  - `archivo.sql`: base schema (operational domain tables).
  - `modificaciones.sql`: renames/migrations (e.g., `USUARIOS -> CLIENTES`, `PEDIDO -> FACTURAS`).
  - `datos.sql`: large simulation dataset aligned to renamed business tables.
- Runtime configuration is environment-driven in `config.py`:
  - `DATABASE_URL` for `SQLALCHEMY_DATABASE_URI`.
  - `SECRET_KEY` for Flask secret configuration.

## Key conventions specific to this codebase

- Use **Spanish domain naming** consistently across routes, services, models, and DB objects (`clientes`, `facturas`, `habeas_data`, `tipo_regimen`).
- Use **business string IDs** (`id_cliente`, etc.) instead of auto-increment integer IDs.
- Keep route modules **thin** and push DB/business rules into `app/services/*`.
- Preserve the **delete guard contract** for clients:
  - Service returns sentinel states (`"no_encontrado"`, `"tiene_facturas"`, `"eliminado"`).
  - Route maps them to HTTP 404 / 409 / 200 respectively.
- In client updates, keep `numero_identificacion` effectively immutable:
  - `actualizar_cliente()` only updates a whitelist of editable fields.
- Optional/default payload behavior is implemented in services with `data.get(...)` defaults; keep that pattern for backward-compatible API behavior.
- Keep DB constraints aligned with application rules:
  - The SQL scripts encode many domain constraints/checks; application changes should stay consistent with those constraints.
