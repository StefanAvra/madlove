// MadLove's page: the start screen, the pause while the page is away and, on touch screens, the
// cabinet's control panel.
//
// The panel imitates the cabinet's joystick. Its state lives in window.madlove_input, which the game
// reads every frame (madlove.controls.VirtualStick) and turns into the same events as the real stick
// and buttons. x and y are -1, 0 or 1, with -1 meaning left or up, as on a joystick.

'use strict';

window.madlove_input = { x: 0, y: 0, start: false, action: false };

(function () {
    const STICK_THRESHOLD = 0.4;  // how far, as a share of the stick zone's radius, a finger has to move
    const BALL_TRAVEL = 0.12;  // how far the ball moves when tilted, as a share of the stick's size

    const params = new URLSearchParams(window.location.search);
    const touch = params.get('touch') === '1' || (params.get('touch') !== '0' && matchMedia('(pointer: coarse)').matches);

    // ---------- the loading progress ----------

    // the cabinet on the start screen fills with colour as the game loads. two downloads take most of
    // the time and run side by side: Python, which pygbag reports through Module.setStatus, and the
    // game's archive, fetched here as soon as the page opens. what comes after, unpacking and starting
    // the game, has no measure and fills the rest at once
    const RUNTIME_SHARE = 0.45;
    const ARCHIVE_SHARE = 0.45;
    const loading = { runtime: 0, archive: 0, done: false };
    let archive = null;  // the archive's bytes once downloaded, or the error

    function show_progress() {
        const share = loading.done ? 1 : RUNTIME_SHARE * loading.runtime + ARCHIVE_SHARE * loading.archive;
        document.documentElement.style.setProperty('--loaded', share);
    }

    async function fetch_archive() {
        // pygbag's own download has no progress
        const name = window.config.archive + (location.host.includes('.itch.zone') ? '.apk' : '.tar.gz');
        try {
            const response = await fetch(name);
            if (!response.ok) throw new Error(`${name}: ${response.status}`);
            const size = Number(response.headers.get('Content-Length'));  // 0 if unknown
            const reader = response.body.getReader();
            const chunks = [];
            let received = 0;
            for (;;) {
                const { done, value } = await reader.read();
                if (done) break;
                chunks.push(value);
                received += value.length;
                if (size) {
                    loading.archive = Math.min(received / size, 1);
                    show_progress();
                }
            }
            archive = new Uint8Array(received);
            let at = 0;
            for (const chunk of chunks) {
                archive.set(chunk, at);
                at += chunk.length;
            }
        } catch (error) {
            console.error('madlove.js: could not download the archive', error);
            archive = error;
        }
        loading.archive = 1;
        show_progress();
    }
    fetch_archive();

    // ---------- the music ----------

    const MUSIC_TRIES = 3;
    const MUSIC_RETRY = 2000;  // milliseconds before trying a track again

    async function download_music(folder, names) {
        for (const name of names) {
            const url = `music/${name}.ogg`;
            for (let tries = 1; ; tries++) {
                try {
                    const response = await fetch(url);
                    if (!response.ok) throw new Error(`${url}: ${response.status}`);
                    const bytes = new Uint8Array(await response.arrayBuffer());
                    // all at once, so Python never finds half a file
                    window.FS.writeFile(`${folder}/${name}.ogg`, bytes);
                    break;
                } catch (error) {
                    if (tries >= MUSIC_TRIES) {
                        console.error('madlove.js: could not download the music', error);  // it stays silent
                        break;
                    }
                    await new Promise((resolve) => setTimeout(resolve, MUSIC_RETRY));
                }
            }
        }
    }

    // pygbag sets window.Module when it starts Python
    const hook = setInterval(() => {
        const module = window.Module;
        if (!module || !module.setStatus) return;
        clearInterval(hook);
        const set_status = module.setStatus;
        module.setStatus = function (text) {
            const counts = /\((\d+)\/(\d+)\)/.exec(text);  // "Downloading data... (loaded/total)"
            if (counts) loading.runtime = Math.min(counts[1] / counts[2], 1);
            else if (text === 'Running...') loading.runtime = 1;
            show_progress();
            return set_status.apply(this, arguments);
        };
    }, 20);

    // ---------- the frame rate ----------

    // at 30 frames per second the game shows every other step of its 60 a second (madlove.game), so the
    // ball and the paddle jump. iOS's Low Power Mode holds Safari at 30, and no browser tells a page about
    // it, so the start screen measures the time between frames and asks the player to turn it off. a page that is
    // busy loading also misses frames, but then their times vary; a capped one shows almost only frames
    // of about 33 ms
    const FRAMES_MEASURED = 30;
    const CAPPED_SHARE = 0.75;  // of the frames measured, how many have to look capped
    const CAPPED_MIN = 30;  // milliseconds; 33.3 at 30 frames per second
    const CAPPED_MAX = 37;
    const FULL_SPEED_MAX = 22;  // a median below this, about 45 frames per second and up, is full speed
    const FRAME_GAP = 100;  // longer gaps are the page being away or blocked, not the frame rate

    // ?fps=1 in the URL shows what is measured, in the top left corner, and goes on measuring in the game
    const SHOW_FPS = params.get('fps') === '1';
    const FPS_LINES = 8;  // the batches shown, the newest at the top

    let frame_times = [];
    let last_frame = 0;
    let gaps = 0;  // frames left out for being longer than FRAME_GAP, in the current batch
    let measuring = 0;  // the pending animation frame, 0 once the game runs
    let fps_lines = [];

    function measure(time) {
        measuring = requestAnimationFrame(measure);
        const interval = time - last_frame;
        last_frame = time;
        if (interval > FRAME_GAP) gaps++;
        if (interval <= 0 || interval > FRAME_GAP) return;
        frame_times.push(interval);
        if (frame_times.length < FRAMES_MEASURED) return;
        const capped = frame_times.filter((t) => t >= CAPPED_MIN && t <= CAPPED_MAX).length;
        const sorted = frame_times.slice().sort((a, b) => a - b);
        const median = sorted[FRAMES_MEASURED >> 1];
        const warning = document.getElementById('start-warning');
        if (capped >= CAPPED_SHARE * FRAMES_MEASURED) warning.hidden = false;
        else if (median < FULL_SPEED_MAX) warning.hidden = true;  // back from turning it off
        if (SHOW_FPS) {
            const ms = (t) => t.toFixed(1).padStart(5);
            fps_lines.unshift(
                `${Math.round(1000 / median).toString().padStart(3)} FPS` +
                ` MED${ms(median)} MIN${ms(sorted[0])} MAX${ms(sorted[FRAMES_MEASURED - 1])}` +
                ` CAP${Math.round((100 * capped) / FRAMES_MEASURED).toString().padStart(4)}%` +
                ` GAPS ${gaps} ${warning.hidden ? '' : 'WARN'}`,
            );
            fps_lines = fps_lines.slice(0, FPS_LINES);
            document.getElementById('fps-readout').textContent = fps_lines.join('\n');
        }
        frame_times = [];
        gaps = 0;
    }

    function stop_measuring() {
        if (SHOW_FPS) return;
        cancelAnimationFrame(measuring);
        measuring = 0;
    }

    // ---------- the start screen ----------

    window.madlove_page = {
        active: true,  // false while the page is hidden or has lost focus; the game and the CRT then stop
        // Python calls this until it returns 1, when the archive is written to path; -1 if the download failed
        save_archive(path) {
            if (archive === null) return 0;
            if (archive instanceof Error) return -1;
            window.FS.writeFile(path, archive);
            archive = new Uint8Array(0);  // let go of the bytes; Python has them now
            loading.runtime = 1;
            show_progress();
            return 1;
        },
        // Python calls this when the game is loaded but the browser still needs a click, tap or key
        ready() {
            loading.done = true;
            show_progress();
            const start = document.getElementById('start');
            start.classList.add('ready');
            document.getElementById('start-text').textContent = touch ? 'TAP TO PLAY' : 'CLICK OR PRESS ANY KEY';
        },
        // Python calls this when the game starts, with the folder of its music and, as JSON, the tracks
        // that aren't in the archive. they download one after the other, in the order the game first
        // plays them, from music/ next to this page; madlove.audio plays each once it's there
        fetch_music(folder, names) {
            download_music(folder, JSON.parse(names));
        },
        // Python calls this when the game runs
        started() {
            loading.done = true;
            show_progress();
            document.getElementById('start').classList.add('gone');
            stop_measuring();
            window.madlove_crt.start();
        },
    };

    function unlock_sound() {
        // pygbag waits for this flag before it starts the game; any click, tap or key counts as the
        // player's permission to play sound. pygbag's own sound test can reset it while loading, so
        // every event sets it again
        if (window.MM) window.MM.UME = true;
    }
    window.addEventListener('pointerdown', unlock_sound, true);
    window.addEventListener('keydown', unlock_sound, true);

    // ---------- the pause while the page is away ----------

    // a phone got hot with the game left open in a tab, so nothing runs while the page is hidden or
    // something else has the focus. the game (madlove.game.Game.run) stops and pauses its sound, and
    // comes back in the smoke break if a level was running
    const releasers = [];  // let go of the stick and the buttons, so nothing stays held after the pause

    function update_active() {
        const active = document.visibilityState === 'visible' && document.hasFocus();
        if (active === window.madlove_page.active) return;
        window.madlove_page.active = active;
        // SDL's sound keeps running on the page's main thread even when paused, so stop it too
        const sound = window.Module && window.Module.SDL2 && window.Module.SDL2.audioContext;
        if (active) {
            window.madlove_crt.resume();
            if (sound) sound.resume();
        } else {
            window.madlove_crt.pause();
            if (sound) sound.suspend();
            for (const release of releasers) release();
        }
    }
    document.addEventListener('visibilitychange', update_active);
    for (const type of ['pagehide', 'pageshow', 'blur', 'focus']) window.addEventListener(type, update_active);

    // ---------- the control panel ----------

    function buzz() {
        if (navigator.vibrate) navigator.vibrate(10);
    }

    function setup_stick() {
        const zone = document.getElementById('stick-zone');
        const stick = document.getElementById('stick');
        const ball = document.getElementById('stick-ball');
        const shaft = document.getElementById('stick-shaft');
        let pointer = null;

        function show(x, y) {
            // the ball moves toward the direction; the shaft runs from the washer to the ball
            const size = stick.clientWidth;
            const length = Math.hypot(x, y) || 1;
            const dx = (x / length) * BALL_TRAVEL * size * (x !== 0);
            const dy = (y / length) * BALL_TRAVEL * size * (y !== 0) * 0.6;  // seen from above at an angle
            ball.style.setProperty('--x', dx + 'px');
            ball.style.setProperty('--y', dy + 'px');
            const rise = 0.38 * size - dy;  // from the washer up to the ball's centre
            const angle = Math.atan2(dx, rise);
            shaft.style.height = Math.hypot(dx, rise) + 'px';
            shaft.style.transform = `translate(-50%, -100%) rotate(${angle}rad)`;
            shaft.style.transformOrigin = '50% 100%';
        }

        function set(x, y) {
            const input = window.madlove_input;
            if (x !== input.x || y !== input.y) {
                if (x || y) buzz();
                input.x = x;
                input.y = y;
                show(x, y);
            }
        }

        function move(event) {
            const box = stick.getBoundingClientRect();
            const radius = box.width / 2;
            const nx = (event.clientX - (box.left + radius)) / radius;
            const ny = (event.clientY - (box.top + radius)) / radius;
            const x = nx > STICK_THRESHOLD ? 1 : nx < -STICK_THRESHOLD ? -1 : 0;
            const y = ny > STICK_THRESHOLD ? 1 : ny < -STICK_THRESHOLD ? -1 : 0;
            set(x, y);
        }

        function release(event) {
            if (event.pointerId !== pointer) return;
            pointer = null;
            set(0, 0);
        }
        releasers.push(() => {
            pointer = null;
            set(0, 0);
        });

        zone.addEventListener('pointerdown', (event) => {
            event.preventDefault();
            pointer = event.pointerId;
            zone.setPointerCapture(pointer);
            move(event);
        });
        zone.addEventListener('pointermove', (event) => {
            if (event.pointerId === pointer) move(event);
        });
        zone.addEventListener('pointerup', release);
        zone.addEventListener('pointercancel', release);
        zone.addEventListener('lostpointercapture', release);

        show(0, 0);
        window.addEventListener('resize', () => show(window.madlove_input.x, window.madlove_input.y));
    }

    function setup_buttons() {
        for (const cell of document.querySelectorAll('.button-cell')) {
            const name = cell.dataset.button;  // 'start' or 'action'
            const button = cell.querySelector('.arcade-button');
            let pointer = null;

            function let_go() {
                pointer = null;
                button.classList.remove('pressed');
                window.madlove_input[name] = false;
            }
            releasers.push(let_go);

            function release(event) {
                if (event.pointerId === pointer) let_go();
            }

            cell.addEventListener('pointerdown', (event) => {
                event.preventDefault();
                pointer = event.pointerId;
                cell.setPointerCapture(pointer);
                button.classList.add('pressed');
                window.madlove_input[name] = true;
                buzz();
            });
            cell.addEventListener('pointerup', release);
            cell.addEventListener('pointercancel', release);
            cell.addEventListener('lostpointercapture', release);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        if (touch) document.body.classList.add('touch');
        setup_stick();
        setup_buttons();
        update_active();
        if (SHOW_FPS) {
            const readout = document.createElement('pre');
            readout.id = 'fps-readout';
            readout.textContent = 'MEASURING';
            document.body.appendChild(readout);
        }
        measuring = requestAnimationFrame(measure);
        // no long-press menu anywhere on the page
        document.addEventListener('contextmenu', (event) => event.preventDefault());
    });
})();
