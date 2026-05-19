import re
with open('d:\\project_amanix\\amanix\\app\\templates\\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'class="footer"', 'class="footer fade-in-up"', content)

with open('d:\\project_amanix\\amanix\\app\\templates\\index.html', 'w', encoding='utf-8') as f:
    f.write(content)
