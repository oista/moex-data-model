
# html
cd c:\Users\bons1\IdeaProjects\moex-data-model
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-viewer.ps1

# semantic-diff
moex-model semantic-diff --left a.yaml --right b.yaml --json
