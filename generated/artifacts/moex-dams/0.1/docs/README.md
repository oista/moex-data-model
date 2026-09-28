# DAMS gen-doc (LinkML)

Full Markdown set is produced by `make generate-artifacts` (or `moex-model compile --artifacts`).

**Git policy (`index_subset`):** only this `README.md` and `index.md` are committed.
Other `*.md` files are gitignored; regenerate locally or in CI for the full tree.
The golden `content_digest` in `generated/manifests/moex-dams-doc.json` covers the **full** generated tree (this README is written after digest and is not part of it).

Before `make generate-bundle` with staging, run a full doc generate so the staged bundle includes all pages.
