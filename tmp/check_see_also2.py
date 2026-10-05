from pathlib import Path
import urllib.request
html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=30).read().decode("utf-8", errors="replace")
idx = html.find("modules =")
print(repr(html[idx:idx+200]))
idx2 = html.find("see_also")
print("see_also context", repr(html[idx2-80:idx2+200]))
# count see_also occurrences near glossary
print("see_also count", html.count("see_also"))
print("range: count", html.count("range:"))
