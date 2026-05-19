import sys

file_path = 'd:/project_amanix/amanix/app/templates/songs_list.html'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_content = """        function switchMainView(viewId) {
            document.getElementById('homeView').style.display = 'none';
            document.getElementById('libraryView').style.display = 'none';
            const pdView = document.getElementById('playlistDetailView');
            if(pdView) pdView.style.display = 'none';
            
            document.getElementById('navHome').classList.remove('active');
            document.getElementById('navLibrary').classList.remove('active');
            
            document.getElementById(viewId + 'View').style.display = 'block';
            if(viewId === 'home') document.getElementById('navHome').classList.add('active');
            if(viewId === 'library') document.getElementById('navLibrary').classList.add('active');
            
            window.scrollTo({top: 0, behavior: 'smooth'});
        }

        // Initial queue load
        const allSongs = [
            {% for song in songs %}
            {
                id: '{{ song.song_id }}',
                title: '{{ song.title|escapejs }}',
                artist: '{% if song.singers.all %}{% for s in song.singers.all %}{{ s.artist_name|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}{% else %}Unknown Artist{% endif %}',
                cover: '{% if song.cover_image %}{{ song.cover_image.url }}{% else %}{% static "images/logo/LOGO3.png" %}{% endif %}',
                audio: '{% if song.audio_file %}{{ song.audio_file.url }}{% else %}none{% endif %}',
                duration: '{% if song.duration %}{{ song.duration }}{% else %}0:00{% endif %}',
                liked: {% if song.song_id in liked_song_ids %}true{% else %}false{% endif %},
                lyrics: '{% if song.lyrics %}{{ song.lyrics|escapejs }}{% else %}Lyrics not available{% endif %}'
            }{% if not forloop.last %},{% endif %}
            {% endfor %}
        ];

        const userPlaylists = {
            {% for playlist in user_playlists %}
            '{{ playlist.id }}': [
                {% for ps in playlist.songs.all %}
                '{{ ps.song.song_id }}'{% if not forloop.last %},{% endif %}
                {% endfor %}
            ]{% if not forloop.last %},{% endif %}
            {% endfor %}
        };

        function openLikedMusic() {
            const likedSongs = allSongs.filter(s => s.liked);
            renderPlaylistDetail('Liked music', 'Auto playlist', 'linear-gradient(135deg, #a855f7, #ec4899)', 'fa-thumbs-up', likedSongs);
        }

        function openPlaylist(id, title) {
            const songIds = userPlaylists[id] || [];
            const playlistSongs = allSongs.filter(s => songIds.includes(s.id));
            renderPlaylistDetail(title, 'Playlist', 'linear-gradient(135deg, #3b82f6, #8b5cf6)', 'fa-music', playlistSongs);
        }

        function renderPlaylistDetail(title, subtitle, bg, icon, songsList) {
            document.getElementById('libraryView').style.display = 'none';
            document.getElementById('playlistDetailView').style.display = 'block';
            
            document.getElementById('playlistDetailTitle').textContent = title;
            document.getElementById('playlistDetailCount').textContent = songsList.length;
            
            const coverEl = document.getElementById('playlistDetailCover');
            coverEl.style.background = bg;
            coverEl.innerHTML = `<i class="fas ${icon}" style="color:#fff; font-size:64px;"></i>`;
            
            const listEl = document.getElementById('playlistDetailList');
            listEl.innerHTML = '';
            
            if (songsList.length === 0) {
                listEl.innerHTML = '<div style="color: #aaa; padding: 20px 0;">No songs in this playlist.</div>';
            } else {
                songsList.forEach((s, idx) => {
                    const item = document.createElement('div');
                    item.className = 'q-item';
                    item.style.marginBottom = '8px';
                    
                    item.innerHTML = `
                        <div class="q-item-img"><img src="${s.cover}" alt="cover"></div>
                        <div class="q-info">
                            <div class="q-title">${s.title}</div>
                            <div class="q-artist">${s.artist}</div>
                        </div>
                        <div class="q-duration">${s.duration}</div>
                        <div style="padding: 0 10px; color: #aaa; cursor: pointer; transition: color 0.3s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#aaa'" onclick="showContextMenu(event, '${s.id}')"><i class="fas fa-ellipsis-v"></i></div>
                    `;
                    item.onclick = (e) => {
                        if(e.target.closest('.fa-ellipsis-v')) return;
                        queue = [...songsList];
                        cIndex = idx;
                        loadAndPlay();
                        if(!isPlayerView) toggleView();
                    };
                    listEl.appendChild(item);
                });
            }
            
            const playBtn = document.getElementById('playlistDetailPlayBtn');
            playBtn.onclick = () => {
                if(songsList.length > 0) {
                    queue = [...songsList];
                    cIndex = 0;
                    loadAndPlay();
                    if(!isPlayerView) toggleView();
                }
            };
        }

        let toastTimeout;
        function showToast(msg) {
            let toastEl = document.getElementById('yt-toast');
            if(!toastEl) {
                toastEl = document.createElement('div');
                toastEl.id = 'yt-toast';
                document.body.appendChild(toastEl);
            }
            toastEl.textContent = msg;
            toastEl.classList.add('show');
            clearTimeout(toastTimeout);
            toastTimeout = setTimeout(() => {
                toastEl.classList.remove('show');
            }, 3000);
        }

        function playSong(id) {
            const songObj = allSongs.find(s => s.id == id);
            if(!songObj) { showToast("Song not found."); return; }
            if(songObj.audio === 'none' || !songObj.audio) { showToast("Audio not available."); return; }
            
            // Check if exists in queue
            let idx = queue.findIndex(s => s.id == id);
            if(idx === -1) {
                queue.push(songObj);
                idx = queue.length - 1;
            }
            cIndex = idx;
            loadAndPlay();
            
            // Auto open player view on first play
            if(!isPlayerView) toggleView();
        }
"""

lines[733:754] = [new_content + '\n']

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
