FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git curl ca-certificates \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://mise.run | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY assets/ /app/assets/
COPY scripts/ /app/scripts/
COPY workflows/ /app/workflows/
COPY mise.toml /app/mise.toml
RUN rm -rf /app/comfy 2>/dev/null || true

RUN mise run setup

EXPOSE 8188

CMD ["mise", "run", "start_cheap"]