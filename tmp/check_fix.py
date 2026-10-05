import urllib.request
html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=30).read().decode("utf-8", errors="replace")
print("toolbar above", "Toolbar above the split" in html)
print("emptyNeighboursMessage", "emptyNeighboursMessage" in html)
print("grid-template-rows auto", "grid-template-rows: auto minmax(200px, 1fr) minmax(200px, 1fr)" in html)
