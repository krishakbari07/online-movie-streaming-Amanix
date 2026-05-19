import sys

file_path = 'd:/project_amanix/amanix/app/templates/songs_list.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = '''                <div class="fp-queue-header" id="fpQueueHeader">
                    <div>
                        <div class="playing-from">Playing from</div>
                        <div class="queue-title">Your Queue</div>
                    </div>
                </div>'''

replacement1 = '''                <div class="fp-queue-header" id="fpQueueHeader" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 20px;">
                    <div>
                        <div class="playing-from">Playing from</div>
                        <div class="queue-title">Your Queue</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 20px;">
                        <span style="font-size: 13px; color: #fff; font-weight: 500;">Autoplay</span>
                        <input type="checkbox" id="autoPlayToggle" checked style="cursor:pointer; accent-color: var(--yt-brand);">
                    </div>
                </div>'''

target2 = '''        function playNext() { 
            if(queue.length === 0) return;
            if(repeatMode === 2) {
                audio.currentTime = 0;
                audio.play();
                return;
            }
            if(isShuffle) {
                let nextIdx = Math.floor(Math.random() * queue.length);
                if(nextIdx === cIndex && queue.length > 1) nextIdx = (nextIdx + 1) % queue.length;
                cIndex = nextIdx;
                loadAndPlay();
            } else {
                if(cIndex < queue.length - 1) { 
                    cIndex++; 
                    loadAndPlay(); 
                } else { 
                    if(repeatMode === 1) {
                        cIndex = 0;
                        loadAndPlay();
                    } else {
                        audio.pause(); 
                        document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>'; 
                        document.getElementById('fpArtWrapper').classList.remove('spinning');
                        audio.currentTime=0;
                    }
                } 
            }
        }'''

replacement2 = '''        function playNext() { 
            if(queue.length === 0) return;
            if(repeatMode === 2) {
                audio.currentTime = 0;
                audio.play();
                return;
            }
            if(isShuffle) {
                let nextIdx = Math.floor(Math.random() * queue.length);
                if(nextIdx === cIndex && queue.length > 1) nextIdx = (nextIdx + 1) % queue.length;
                cIndex = nextIdx;
                loadAndPlay();
            } else {
                if(cIndex < queue.length - 1) { 
                    cIndex++; 
                    loadAndPlay(); 
                } else { 
                    if(repeatMode === 1) {
                        cIndex = 0;
                        loadAndPlay();
                    } else {
                        const autoPlayToggle = document.getElementById('autoPlayToggle');
                        if (autoPlayToggle && autoPlayToggle.checked) {
                            const currentSong = queue[cIndex];
                            let nextSongPool = allSongs.filter(s => s.artist === currentSong.artist && s.id !== currentSong.id && !queue.find(qs => qs.id === s.id));
                            if (nextSongPool.length === 0) {
                                nextSongPool = allSongs.filter(s => !queue.find(qs => qs.id === s.id));
                            }
                            if (nextSongPool.length > 0) {
                                const randomNext = nextSongPool[Math.floor(Math.random() * nextSongPool.length)];
                                queue.push(randomNext);
                                cIndex++;
                                loadAndPlay();
                                showToast("Autoplaying next song");
                            } else {
                                audio.pause(); 
                                document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>'; 
                                document.getElementById('fpArtWrapper').classList.remove('spinning');
                                audio.currentTime=0;
                            }
                        } else {
                            audio.pause(); 
                            document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>'; 
                            document.getElementById('fpArtWrapper').classList.remove('spinning');
                            audio.currentTime=0;
                        }
                    }
                } 
            }
        }'''

if target1 in content:
    content = content.replace(target1, replacement1)
    print('Replaced target 1')
else:
    print('Target 1 not found')

if target2 in content:
    content = content.replace(target2, replacement2)
    print('Replaced target 2')
else:
    print('Target 2 not found')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
