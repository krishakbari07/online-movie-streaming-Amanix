import sys

file_path = 'd:/project_amanix/amanix/app/templates/songs_list.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = '''            likeBtn.className = s.liked ? 'bp-btn bp-like liked' : 'bp-btn bp-like';
            
            renderQueue();'''

replacement1 = '''            likeBtn.className = s.liked ? 'bp-btn bp-like liked' : 'bp-btn bp-like';
            
            const autoPlayToggle = document.getElementById('autoPlayToggle');
            if (autoPlayToggle && autoPlayToggle.checked && allSongs.length > 1) {
                while (queue.length - 1 - cIndex < 10) {
                    const currentLastSong = queue[queue.length - 1];
                    let nextSongPool = allSongs.filter(rs => rs.artist === currentLastSong.artist && rs.id !== currentLastSong.id && !queue.find(qs => qs.id === rs.id));
                    if (nextSongPool.length === 0) {
                        nextSongPool = allSongs.filter(rs => !queue.find(qs => qs.id === rs.id));
                    }
                    if (nextSongPool.length === 0) {
                        nextSongPool = allSongs.filter(rs => rs.id !== currentLastSong.id);
                    }
                    if (nextSongPool.length > 0) {
                        queue.push(nextSongPool[Math.floor(Math.random() * nextSongPool.length)]);
                    } else {
                        break;
                    }
                }
            }
            
            renderQueue();'''

if target1 in content:
    content = content.replace(target1, replacement1)
    print('Replaced target 1')
else:
    print('Target 1 not found')


target2 = '''        function playPrev() { if(audio.currentTime > 3) audio.currentTime = 0; else if(cIndex > 0) { cIndex--; loadAndPlay(); } }'''

replacement2 = '''        function playPrev() { if(audio.currentTime > 3) audio.currentTime = 0; else if(cIndex > 0) { cIndex--; loadAndPlay(); } }
        
        document.addEventListener('DOMContentLoaded', () => {
            const autoPlayToggle = document.getElementById('autoPlayToggle');
            if (autoPlayToggle) {
                autoPlayToggle.addEventListener('change', () => {
                    if (autoPlayToggle.checked) {
                        loadAndPlay(); // Triggers the auto-populate logic and re-renders queue
                    }
                });
            }
        });'''

if target2 in content:
    content = content.replace(target2, replacement2)
    print('Replaced target 2')
else:
    print('Target 2 not found')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
