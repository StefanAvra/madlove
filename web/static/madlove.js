// MadLove's page: the start screen and, on touch screens, the cabinet's control panel.
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

    // ---------- the start screen ----------

    window.madlove_page = {
        // Python calls this when the game is loaded but the browser still needs a click, tap or key
        ready() {
            const start = document.getElementById('start');
            start.classList.add('ready');
            document.getElementById('start-text').textContent = touch ? 'TAP TO PLAY' : 'CLICK OR PRESS ANY KEY';
        },
        // Python calls this when the game runs
        started() {
            document.getElementById('start').classList.add('gone');
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
        for (const button of document.querySelectorAll('.arcade-button')) {
            const name = button.dataset.button;  // 'start' or 'action'
            let pointer = null;

            function release(event) {
                if (event.pointerId !== pointer) return;
                pointer = null;
                button.classList.remove('pressed');
                window.madlove_input[name] = false;
            }

            button.addEventListener('pointerdown', (event) => {
                event.preventDefault();
                pointer = event.pointerId;
                button.setPointerCapture(pointer);
                button.classList.add('pressed');
                window.madlove_input[name] = true;
                buzz();
            });
            button.addEventListener('pointerup', release);
            button.addEventListener('pointercancel', release);
            button.addEventListener('lostpointercapture', release);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        if (touch) document.body.classList.add('touch');
        setup_stick();
        setup_buttons();
        // no long-press menu anywhere on the page
        document.addEventListener('contextmenu', (event) => event.preventDefault());
    });
})();
