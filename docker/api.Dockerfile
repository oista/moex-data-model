# Application image: API, CLI, viewer builder. Model files are not copied.
# Editable installs keep source on disk so a later overlay can replace it.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    MOEX_IMAGE_CONTRACTS_MANIFEST=/app/generated/manifests/moex-dams-contracts.json

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY generated/contracts/moex-dams/0.1 ./generated/contracts/moex-dams/0.1
COPY generated/manifests ./generated/manifests
COPY packages/modeling-kernel ./packages/modeling-kernel
COPY packages/standard-linkml ./packages/standard-linkml
COPY packages/specification-dams ./packages/specification-dams
COPY packages/semantic-mappings ./packages/semantic-mappings
COPY packages/linkml-tooling ./packages/linkml-tooling
COPY packages/external-sources ./packages/external-sources
COPY packages/publication ./packages/publication
COPY packages/repository-loader ./packages/repository-loader
COPY packages/git-adapter ./packages/git-adapter
COPY packages/drawdb-adapter ./packages/drawdb-adapter
COPY apps/api ./apps/api
COPY apps/cli ./apps/cli
COPY apps/viewer ./apps/viewer

RUN pip install --upgrade pip \
    && pip install \
        -e ./generated/contracts/moex-dams/0.1 \
        -e ./packages/modeling-kernel \
        -e ./packages/standard-linkml \
        -e ./packages/specification-dams \
        -e ./packages/semantic-mappings \
        -e ./packages/linkml-tooling \
        -e ./packages/external-sources \
        -e ./packages/publication \
        -e ./packages/repository-loader \
        -e ./packages/git-adapter \
        -e ./packages/drawdb-adapter \
        -e ./apps/cli \
        -e ./apps/api \
        -e ./apps/viewer \
    && mkdir -p /models /data /viewer-dist /app/docker \
    && useradd --create-home --uid 10001 moex \
    && chown -R moex:moex /app /models /data /viewer-dist

COPY docker/models-sync.sh ./docker/models-sync.sh
RUN sed -i 's/\r$//' /app/docker/models-sync.sh \
    && chmod 755 /app/docker/models-sync.sh

# Editable installs accept linkml>=1.7,<2, which currently resolves to 1.12.
# 1.12 imports linkml_runtime.utils.rdf_canonicalize, missing from the
# viewer's pin linkml-runtime==1.11.1. Stay on the toolchain in
# requirements-linkml.txt so publish-gate can import inside this image.
RUN pip install "linkml==1.11.1" "linkml-runtime==1.11.1"

USER moex

ARG DEPS_FINGERPRINT=
ARG MOEX_VERSION=
ARG GIT_SHA=
LABEL moexmodel.deps_fingerprint="${DEPS_FINGERPRINT}" \
      moexmodel.full_version="${MOEX_VERSION}" \
      moexmodel.git_sha="${GIT_SHA}"

EXPOSE 8000

CMD ["python", "-m", "moex_model_api"]
