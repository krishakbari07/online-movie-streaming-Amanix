import sys

file_path = 'd:/project_amanix/amanix/app/templates/movie.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace HTML
html_target = '''                    <div class="custom-controls">
                        <div class="progress-container" id="progressContainer">
                            <div class="progress-bar" id="progressBar"></div>
                        </div>
                        <div class="controls-main">
                            <div class="controls-left">
                                <button class="control-btn" id="playPauseBtn"><i class="fa-solid fa-play"></i></button>
                                <button class="control-btn" id="rewindBtn"><i class="fa-solid fa-backward-step"></i></button>
                                <button class="control-btn" id="forwardBtn"><i class="fa-solid fa-forward-step"></i></button>
                                <div class="volume-container">
                                    <button class="control-btn" id="muteBtn"><i class="fa-solid fa-volume-high"></i></button>
                                    <input type="range" class="volume-slider" id="volumeSlider" min="0" max="1" step="0.05" value="1">
                                </div>
                                <div class="time-display">
                                    <span id="currentTime">00:00</span> / <span id="durationTime">00:00</span>
                                </div>
                            </div>
                            <div class="controls-right">
                                <div style="position:relative;">
                                    <button class="control-btn" id="speedBtn" style="font-size: 1rem; font-weight: bold;">1x</button>
                                    <div class="speed-menu" id="speedMenu">
                                        <div class="speed-option" data-speed="0.5">0.5x</div>
                                        <div class="speed-option" data-speed="0.75">0.75x</div>
                                        <div class="speed-option active" data-speed="1">1x</div>
                                        <div class="speed-option" data-speed="1.25">1.25x</div>
                                        <div class="speed-option" data-speed="1.5">1.5x</div>
                                        <div class="speed-option" data-speed="2">2x</div>
                                    </div>
                                </div>
                                <button class="control-btn" id="pipBtn"><i class="fa-solid fa-clone"></i></button>
                                <button class="control-btn" id="fullscreenBtn"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                    </div>'''

html_replacement = '''                    <div class="custom-controls">
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
                    </div>'''

# CSS update
css_target = '''        .progress-container {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            cursor: pointer;
            position: relative;
            margin-bottom: 10px;
            transition: height 0.2s;
        }'''

css_replacement = '''        .progress-container {
            flex: 1;
            height: 6px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            cursor: pointer;
            position: relative;
            margin: 0 15px;
            transition: height 0.2s;
        }'''

css_target_main = '''        .controls-main {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }'''

css_replacement_main = '''        .controls-main {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            gap: 12px;
            width: 100%;
        }'''


if html_target in content:
    content = content.replace(html_target, html_replacement)
    print("HTML Replaced")
else:
    print("HTML Target not found")

if css_target in content:
    content = content.replace(css_target, css_replacement)
    print("CSS Replaced")
else:
    print("CSS Target not found")

if css_target_main in content:
    content = content.replace(css_target_main, css_replacement_main)
    print("CSS Main Replaced")
else:
    print("CSS Main Target not found")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
