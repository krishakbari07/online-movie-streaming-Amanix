import sys

file_path = 'd:/project_amanix/amanix/app/templates/songs_list.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = '''                <div class="fp-queue-header" id="fpQueueHeader">
                    <div>
                        <div class="playing-from">Playing from</div>
                        <div class="queue-title">Your Queue</div>
                    </div>
                    <button class="save-btn" onclick="showToast('Playlist saved to library!')"><i class="far fa-save"></i> Save</button>
                </div>'''

replacement1 = '''                <div class="fp-queue-header" id="fpQueueHeader" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 20px;">
                    <div>
                        <div class="playing-from">Playing from</div>
                        <div class="queue-title">Your Queue</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 20px;">
                            <span style="font-size: 13px; color: #fff; font-weight: 500;">Autoplay</span>
                            <input type="checkbox" id="autoPlayToggle" checked style="cursor:pointer; accent-color: var(--yt-brand);">
                        </div>
                        <button class="save-btn" onclick="showToast('Playlist saved to library!')"><i class="far fa-save"></i> Save</button>
                    </div>
                </div>'''

if target1 in content:
    content = content.replace(target1, replacement1)
    print('Replaced target 1')
else:
    print('Target 1 not found')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
