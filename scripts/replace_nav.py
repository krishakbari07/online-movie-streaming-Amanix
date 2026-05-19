import os
import re

template_dir = r"d:\project_amanix\amanix\app\templates"

# Regex for finding <nav class="navbar">... matching closing </nav>
regex_navbar = re.compile(r'<nav class="navbar">.*?</nav>', re.DOTALL)
# Regex for finding <nav class="sidebar">...</nav>
regex_sidebar = re.compile(r'<nav class="sidebar">.*?</nav>', re.DOTALL)

for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html') and file != 'navbar.html':
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # replace the navbar classes
            replacement = "{% include 'navbar.html' %}"
            content = regex_navbar.sub(replacement, content)
            
            # if we are in index.html, we also need to remove profile popup and its script, since it's now in navbar.html.
            if file == 'index.html':
                content = regex_sidebar.sub(replacement, content)
                # Remove profile popup div
                profile_re = re.compile(r'<div class="profile" id="pro">.*?</div>\n\s*</div>', re.DOTALL)
                
                # Manual matching for index.html profile popup:
                # It goes <div class="profile" id="pro"> ... <div class="profile_logout">...</div> </div> </div>
                content = re.sub(r'<div class="profile" id="pro">.*?</script>\s*</html>', r'</html>', content, flags=re.DOTALL)
                # Remove old search overlay scripts
                content = re.sub(r'<!-- Hidden Search Box overlay -->.*?</script>', '', content, flags=re.DOTALL)
                
                # Replace any duplicate load static if navbar.html brings it, but let's let load static sit.
                
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {file}")
