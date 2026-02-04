# ─────────────────────────────────
# Stage 1: Build and install via uv
# ─────────────────────────────────
FROM registry.access.redhat.com/ubi10/ubi-minimal:latest AS build

USER 0

RUN microdnf update -y && microdnf clean all

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy only lock + project metadata first + python version metadata
COPY pyproject.toml uv.lock .python-version ./

# Install dependencies without project code
RUN uv sync --frozen --no-install-project --no-dev

# Copy source last (keeps layer cache intact)
COPY src/ ./src/

# Install the project into .venv
RUN uv sync --frozen --no-dev

# ─────────────────────────────────
# Stage 2: Runtime image
# ─────────────────────────────────
FROM registry.access.redhat.com/ubi10/ubi-minimal:latest AS production

USER 0

RUN microdnf update -y && microdnf clean all

WORKDIR /app

# Copy everything from build stage
COPY --from=build /app /app
COPY --from=build /root/.local/share/uv/python /root/.local/share/uv/python

# Set permissions for runtime user
RUN chown -R 10001:0 /app /root/.local/share/uv \
 && chmod -R g=u /app /root/.local/share/uv

USER 10001

EXPOSE 8000

# Ensure Python and .venv are used correctly
ENV PATH="/app/.venv/bin:/root/.local/share/uv/python/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

WORKDIR /app/src

CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
