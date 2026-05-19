import re
with open('d:\\project_amanix\\amanix\\app\\templates\\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'class="section-trending"', 'class="section-trending fade-in-up"', content)
content = re.sub(r'class="webseries-section"', 'class="webseries-section fade-in-up"', content)
content = re.sub(r'class="section-trending (.*?)"', r'class="section-trending fade-in-up \1"', content)
content = re.sub(r'class="webseries-section (.*?)"', r'class="webseries-section fade-in-up \1"', content)

script = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.fade-in-up').forEach(el => {
        observer.observe(el);
    });
});
</script>
</body>
"""

content = content.replace('</body>', script)

with open('d:\\project_amanix\\amanix\\app\\templates\\index.html', 'w', encoding='utf-8') as f:
    f.write(content)
