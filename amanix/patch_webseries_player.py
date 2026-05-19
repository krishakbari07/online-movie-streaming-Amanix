import sys

file_path = 'd:/project_amanix/amanix/app/templates/webseries/watch_episode.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS Injection
css_target = '''        @media (max-width: 992px) {'''

css_replacement = '''        /* Custom Video Player Controls */
        .video-wrapper {
            position: relative;
            border-radius: 22px 22px 0 0;
            overflow: hidden;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .video-wrapper:hover .custom-controls,
        .video-wrapper.paused .custom-controls {
            opacity: 1;
            transform: translateY(0);
        }

        .custom-controls {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0.5), transparent);
            padding: 40px 20px 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.4s ease;
            z-index: 10;
        }

        .progress-container {
            flex: 1;
            height: 6px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            cursor: pointer;
            position: relative;
            margin: 0 15px;
            transition: height 0.2s;
        }
        .progress-container:hover {
            height: 8px;
        }

        .progress-bar {
            height: 100%;
            background: #e50914;
            border-radius: 4px;
            width: 0%;
            position: relative;
        }
        .progress-bar::after {
            content: '';
            position: absolute;
            right: -6px;
            top: 50%;
            transform: translateY(-50%) scale(0);
            width: 12px;
            height: 12px;
            background: #fff;
            border-radius: 50%;
            transition: transform 0.2s;
        }
        .progress-container:hover .progress-bar::after {
            transform: translateY(-50%) scale(1);
        }

        .controls-main {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            gap: 12px;
            width: 100%;
        }

        .controls-left, .controls-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .control-btn {
            background: transparent;
            border: none;
            color: #fff;
            font-size: 1.2rem;
            cursor: pointer;
            transition: color 0.2s, transform 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .control-btn:hover {
            color: #e50914;
            transform: scale(1.1);
        }

        .time-display {
            font-size: 0.9rem;
            color: #ddd;
            font-family: monospace;
            user-select: none;
        }

        .volume-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .volume-slider {
            width: 0;
            opacity: 0;
            transition: width 0.3s, opacity 0.3s;
            accent-color: #e50914;
            cursor: pointer;
        }
        .volume-container:hover .volume-slider {
            width: 80px;
            opacity: 1;
        }

        .player-title {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #fff;
            font-size: 1.4rem;
            font-weight: 700;
            opacity: 0;
            transition: opacity 0.4s;
            text-shadow: 0 2px 10px rgba(0,0,0,0.8);
            z-index: 10;
        }
        .video-wrapper:hover .player-title,
        .video-wrapper.paused .player-title {
            opacity: 1;
        }

        .play-overlay {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(1.5);
            font-size: 4rem;
            color: rgba(255,255,255,0.8);
            opacity: 0;
            transition: all 0.3s;
            pointer-events: none;
            text-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .play-overlay.show {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }

        /* Speed menu */
        .speed-menu {
            position: absolute;
            bottom: 70px;
            right: 50px;
            background: rgba(10, 10, 10, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 10px 0;
            display: none;
            flex-direction: column;
        }
        .speed-menu.show {
            display: flex;
        }
        .speed-option {
            padding: 8px 20px;
            color: #fff;
            cursor: pointer;
            transition: background 0.2s;
        }
        .speed-option:hover, .speed-option.active {
            background: rgba(229, 9, 20, 0.3);
        }

        @media (max-width: 992px) {'''

# 2. HTML & JS Injection
html_js_target = '''                    <div class="video-wrapper" style="position: relative; display: block; line-height: 0;">
                    {% if is_file_source %}
                    <video id="episodePlayer" controls controlsList="nodownload" autoplay {% if episode.thumbnail %}poster="{{ episode.thumbnail.url }}"{% elif webseries.poster %}poster="{{ webseries.poster.url }}"{% endif %}>
                        <source src="{{ episode.video_file.url }}" type="video/mp4">
                        Your browser does not support HTML5 video.
                    </video>
                    {% else %}
                    <iframe id="episodeEmbed" src="{{ episode.video_url }}" allowfullscreen referrerpolicy="no-referrer"></iframe>
                    {% endif %}
                    <script>
                        function skipEpisodeVideo(seconds) {
                            const video = document.getElementById('episodePlayer');
                            if (video) {
                                video.currentTime += seconds;
                            }
                        }

                        // Add double-click/tap functionality for Netlix-like skipping
                        document.addEventListener("DOMContentLoaded", function() {
                            const wrapper = document.querySelector('.video-wrapper');
                            const video = document.getElementById('episodePlayer');
                            if (!wrapper || !video) return;

                            let lastTap = 0;
                            wrapper.addEventListener('click', function(e) {
                                const currentTime = new Date().getTime();
                                const tapLength = currentTime - lastTap;
                                
                                // Checking for double tap / double click
                                if (tapLength < 300 && tapLength > 0) {
                                    // It's a double tap
                                    const rect = wrapper.getBoundingClientRect();
                                    const clickX = e.clientX - rect.left;
                                    
                                    // If clicked on the left half, rewind. Right half, fast-forward.
                                    if (clickX < rect.width / 2) {
                                        skipEpisodeVideo(-10);
                                    } else {
                                        skipEpisodeVideo(10);
                                    }
                                    e.preventDefault();
                                }
                                lastTap = currentTime;
                            });
                        });
                    </script>
                    </div>'''

html_js_replacement = '''                    <div class="video-wrapper paused" style="position: relative; display: flex; align-items:center; justify-content:center; line-height: 0;">
                    {% if is_file_source %}
                    <div class="player-title">{{ episode.title }}</div>
                    <i class="fa-solid fa-play play-overlay" id="playOverlay"></i>
                    <video id="episodePlayer" controlsList="nodownload" autoplay {% if episode.thumbnail %}poster="{{ episode.thumbnail.url }}"{% elif webseries.poster %}poster="{{ webseries.poster.url }}"{% endif %}>
                        <source src="{{ episode.video_file.url }}" type="video/mp4">
                        Your browser does not support HTML5 video.
                    </video>
                    
                    <div class="custom-controls">
                        <div class="controls-main">
                            <button class="control-btn" id="playPauseBtn"><i class="fa-solid fa-play"></i></button>
                            <button class="control-btn" id="forwardBtn"><i class="fa-solid fa-forward-step"></i></button>
                            
                            <div class="progress-container" id="progressContainer">
                                <div class="progress-bar" id="progressBar"></div>
                            </div>
                            
                            <div class="time-display" style="margin-right: 10px;">
                                <span id="currentTime">00:00</span> / <span id="durationTime">00:00</span>
                            </div>
                            
                            <div class="volume-container">
                                <button class="control-btn" id="muteBtn"><i class="fa-solid fa-volume-high"></i></button>
                                <input type="range" class="volume-slider" id="volumeSlider" min="0" max="1" step="0.05" value="1">
                            </div>
                            
                            <button class="control-btn" id="pipBtn" title="Picture in Picture"><i class="fa-solid fa-compress"></i></button>
                            <button class="control-btn" id="fullscreenBtn" title="Fullscreen"><i class="fa-solid fa-expand"></i></button>
                            
                            <div style="position:relative;">
                                <button class="control-btn" id="speedBtn" title="Settings"><i class="fa-solid fa-gear"></i></button>
                                <div class="speed-menu" id="speedMenu">
                                    <div class="speed-option" data-speed="0.5">0.5x</div>
                                    <div class="speed-option" data-speed="0.75">0.75x</div>
                                    <div class="speed-option active" data-speed="1">Normal</div>
                                    <div class="speed-option" data-speed="1.25">1.25x</div>
                                    <div class="speed-option" data-speed="1.5">1.5x</div>
                                    <div class="speed-option" data-speed="2">2x</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% else %}
                    <iframe id="episodeEmbed" src="{{ episode.video_url }}" allowfullscreen referrerpolicy="no-referrer"></iframe>
                    {% endif %}
                    <script>
                        document.addEventListener("DOMContentLoaded", function() {
                            const wrapper = document.querySelector('.video-wrapper');
                            const video = document.getElementById('episodePlayer');
                            const playPauseBtn = document.getElementById('playPauseBtn');
                            const playOverlay = document.getElementById('playOverlay');
                            const progressContainer = document.getElementById('progressContainer');
                            const progressBar = document.getElementById('progressBar');
                            const currentTimeEl = document.getElementById('currentTime');
                            const durationTimeEl = document.getElementById('durationTime');
                            const muteBtn = document.getElementById('muteBtn');
                            const volumeSlider = document.getElementById('volumeSlider');
                            const fullscreenBtn = document.getElementById('fullscreenBtn');
                            const forwardBtn = document.getElementById('forwardBtn');
                            const pipBtn = document.getElementById('pipBtn');
                            const speedBtn = document.getElementById('speedBtn');
                            const speedMenu = document.getElementById('speedMenu');
                            const speedOptions = document.querySelectorAll('.speed-option');
                            
                            if (!wrapper || !video || !playPauseBtn) return;

                            // Set initial state
                            if (!video.paused) {
                                playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
                                wrapper.classList.remove('paused');
                            }

                            // Formatting time
                            function formatTime(seconds) {
                                if (isNaN(seconds)) return "00:00";
                                const h = Math.floor(seconds / 3600);
                                const m = Math.floor((seconds % 3600) / 60);
                                const s = Math.floor(seconds % 60);
                                if (h > 0) return `${h}:${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
                                return `${m}:${s < 10 ? '0' : ''}${s}`;
                            }

                            // Play / Pause
                            function togglePlay() {
                                if (video.paused) {
                                    video.play();
                                    playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
                                    wrapper.classList.remove('paused');
                                    playOverlay.classList.remove('show');
                                } else {
                                    video.pause();
                                    playPauseBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
                                    wrapper.classList.add('paused');
                                    playOverlay.innerHTML = '<i class="fa-solid fa-pause"></i>';
                                    playOverlay.classList.add('show');
                                    setTimeout(() => playOverlay.classList.remove('show'), 500);
                                }
                            }

                            playPauseBtn.addEventListener('click', togglePlay);
                            video.addEventListener('click', togglePlay);
                            
                            // Progress
                            video.addEventListener('timeupdate', () => {
                                const percent = (video.currentTime / video.duration) * 100;
                                progressBar.style.width = percent + '%';
                                currentTimeEl.textContent = formatTime(video.currentTime);
                            });
                            
                            video.addEventListener('loadedmetadata', () => {
                                durationTimeEl.textContent = formatTime(video.duration);
                            });

                            progressContainer.addEventListener('click', (e) => {
                                const rect = progressContainer.getBoundingClientRect();
                                const pos = (e.clientX - rect.left) / rect.width;
                                video.currentTime = pos * video.duration;
                            });

                            // Volume
                            function toggleMute() {
                                video.muted = !video.muted;
                                updateVolumeIcon();
                            }
                            function updateVolumeIcon() {
                                if(video.muted || video.volume === 0) muteBtn.innerHTML = '<i class="fa-solid fa-volume-xmark"></i>';
                                else if(video.volume < 0.5) muteBtn.innerHTML = '<i class="fa-solid fa-volume-low"></i>';
                                else muteBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
                                volumeSlider.value = video.muted ? 0 : video.volume;
                            }

                            muteBtn.addEventListener('click', toggleMute);
                            volumeSlider.addEventListener('input', (e) => {
                                video.volume = e.target.value;
                                video.muted = e.target.value == 0;
                                updateVolumeIcon();
                            });

                            // Skip
                            forwardBtn.addEventListener('click', () => video.currentTime += 10);

                            // Fullscreen
                            fullscreenBtn.addEventListener('click', () => {
                                if (!document.fullscreenElement) {
                                    wrapper.requestFullscreen().catch(err => console.log(err));
                                    fullscreenBtn.innerHTML = '<i class="fa-solid fa-compress"></i>';
                                } else {
                                    document.exitFullscreen();
                                    fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand"></i>';
                                }
                            });

                            // PIP
                            pipBtn.addEventListener('click', () => {
                                if (document.pictureInPictureElement) {
                                    document.exitPictureInPicture();
                                } else if (document.pictureInPictureEnabled) {
                                    video.requestPictureInPicture();
                                }
                            });

                            // Speed
                            speedBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                speedMenu.classList.toggle('show');
                            });
                            document.addEventListener('click', () => speedMenu.classList.remove('show'));
                            
                            speedOptions.forEach(opt => {
                                opt.addEventListener('click', (e) => {
                                    e.stopPropagation();
                                    speedOptions.forEach(o => o.classList.remove('active'));
                                    opt.classList.add('active');
                                    const speed = parseFloat(opt.getAttribute('data-speed'));
                                    video.playbackRate = speed;
                                    speedBtn.textContent = speed + 'x';
                                    speedMenu.classList.remove('show');
                                });
                            });

                            // Keyboard shortcuts
                            document.addEventListener('keydown', (e) => {
                                if(e.code === 'Space') { e.preventDefault(); togglePlay(); }
                                else if(e.code === 'ArrowRight') { video.currentTime += 10; }
                                else if(e.code === 'ArrowLeft') { video.currentTime -= 10; }
                                else if(e.code === 'KeyF') { fullscreenBtn.click(); }
                                else if(e.code === 'KeyM') { toggleMute(); }
                            });

                            // Netflix-like Double tap
                            let lastTap = 0;
                            wrapper.addEventListener('click', function(e) {
                                // Ignore clicks on controls
                                if (e.target.closest('.custom-controls')) return;
                                
                                const currentTime = new Date().getTime();
                                const tapLength = currentTime - lastTap;
                                
                                if (tapLength < 300 && tapLength > 0) {
                                    const rect = wrapper.getBoundingClientRect();
                                    const clickX = e.clientX - rect.left;
                                    
                                    if (clickX < rect.width / 2) {
                                        video.currentTime -= 10;
                                        playOverlay.innerHTML = '<i class="fa-solid fa-backward-step"></i>';
                                    } else {
                                        video.currentTime += 10;
                                        playOverlay.innerHTML = '<i class="fa-solid fa-forward-step"></i>';
                                    }
                                    playOverlay.classList.add('show');
                                    setTimeout(() => playOverlay.classList.remove('show'), 500);
                                    e.preventDefault();
                                }
                                lastTap = currentTime;
                            });
                            
                            // Hide controls on inactivity
                            let timeout;
                            wrapper.addEventListener('mousemove', () => {
                                wrapper.style.cursor = 'default';
                                document.querySelector('.custom-controls').style.opacity = '1';
                                clearTimeout(timeout);
                                timeout = setTimeout(() => {
                                    if (!video.paused) {
                                        wrapper.style.cursor = 'none';
                                        document.querySelector('.custom-controls').style.opacity = '0';
                                    }
                                }, 3000);
                            });
                        });
                    </script>
                    </div>'''


if css_target in content:
    content = content.replace(css_target, css_replacement)
    print("CSS Replaced")
else:
    print("CSS Target not found")

if html_js_target in content:
    content = content.replace(html_js_target, html_js_replacement)
    print("HTML JS Replaced")
else:
    print("HTML JS Target not found")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
