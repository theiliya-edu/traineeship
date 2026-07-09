FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base
WORKDIR /project
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project

COPY alembic.ini /project/
COPY app/shared /project/app/shared/


FROM base AS api
COPY app/spimex_api/ /project/app/spimex_api/
EXPOSE 8000
CMD ["python", "-m", "app.spimex_api.main"]


FROM base AS parser
COPY app/spimex_parser/ /project/app/spimex_parser/
CMD ["python", "-m", "app.spimex_parser.main"]
