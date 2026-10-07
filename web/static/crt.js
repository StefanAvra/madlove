// MadLove's CRT look. The cabinet showed the game on a CRT turned on its side; here a WebGL canvas on
// top of the game's canvas draws every frame again through a CRT shader: curvature, scanlines and
// the mask. There are two shaders, both from libretro: zfast_crt_geo (crt-zfast.glsl), the default,
// and crt-geom-mini (crt-geom.glsl) with ?crt=geom in the URL. ?crt=0 turns the effect off.
//
// window.madlove_crt.settings holds the shader's settings, which can be changed while the game runs,
// for example from the browser's console. madlove.js pauses the effect while the page is hidden or has
// lost focus.

"use strict";

(function () {
  // each shader's file, and its settings with the uniforms they set
  const SHADERS = {
    zfast: {
      file: "crt-zfast.glsl",
      uniforms: {
        scanlines: "SCANLINE_WEIGHT",
        mask: "MASK_DARK",
        mask_pitch: "MASK_PITCH",
        curve: "CURVE",
        vignette: "VIGNETTE",
        d93: "D93",
      },
      settings: {
        scanlines: 7.0, // how dark the gaps between the scanlines are; 0 turns them off
        mask: 0.3, // how dark the mask's stripes are between them; 0 turns it off
        mask_pitch: 1.0, // the mask's stripes per row of the game's pixels
        curve: 1.0, // 0 for a flat screen
        vignette: 0.7, // how much darker the edges get; 0 for none, above 1 stronger
        d93: 0.0, // 1 for the original shader's bluish white of Japanese CRTs, which turns the red orange
      },
    },
    geom: {
      file: "crt-geom.glsl",
      uniforms: {
        scanlines: "scanline_weight",
        mask: "DOTMASK",
        mask_pitch: "MASK_PITCH",
        curve: "curve_amount",
        corners: "cornersize",
        interlace: "interlace_detect",
      },
      settings: {
        scanlines: 0.4, // how bright the beams are, 0.1 to 0.5
        mask: 0.3, // how strong the magenta and green dot mask is; 0 turns it off
        mask_pitch: 1.0, // the mask's magenta and green pairs per row of the game's pixels
        curve: 0.15, // 0 for a flat screen
        corners: 0.05, // how round the corners are
        interlace: 0.0, // 1 draws every other column in turns, like interlaced video; it flickers
      },
    },
  };

  const choice = new URLSearchParams(window.location.search).get("crt");
  const shader = choice === "0" ? null : SHADERS[choice] || SHADERS.zfast;

  window.madlove_crt = {
    settings: shader ? shader.settings : {},
    start() {}, // madlove.js calls this when the game runs
    pause() {}, // and these when the page goes away and comes back
    resume() {},
  };
  if (!shader) return;

  // the shader reads the game's canvas after SDL has drawn it. WebGL clears a canvas once it is on
  // screen, unless asked to keep the picture, so ask for that when SDL creates its context. SDL's draw
  // calls also tell the shader when there is a new picture: screens at 120 Hz ask for twice as many
  // frames as the game draws
  let game_drew = false;
  const get_context = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, attributes) {
    if (this.id !== "canvas" || (type !== "webgl" && type !== "webgl2"))
      return get_context.call(this, type, attributes);
    attributes = Object.assign({}, attributes, { preserveDrawingBuffer: true });
    const gl = get_context.call(this, type, attributes);
    if (gl) {
      for (const name of ["drawArrays", "drawElements"]) {
        const draw = gl[name];
        gl[name] = function (...args) {
          game_drew = true;
          return draw.apply(this, args);
        };
      }
    }
    return gl;
  };

  const VERTEX_SHADER = `
        attribute vec2 position;
        varying vec2 uv;
        void main() {
            uv = position * 0.5 + 0.5;
            gl_Position = vec4(position, 0.0, 1.0);
        }`;

  function compile(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS))
      throw new Error(gl.getShaderInfoLog(shader));
    return shader;
  }

  function link(gl, fragment_source) {
    const program = gl.createProgram();
    gl.attachShader(program, compile(gl, gl.VERTEX_SHADER, VERTEX_SHADER));
    gl.attachShader(program, compile(gl, gl.FRAGMENT_SHADER, fragment_source));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS))
      throw new Error(gl.getProgramInfoLog(program));
    return program;
  }

  async function start() {
    const game = document.getElementById("canvas");
    const crt = document.createElement("canvas");
    crt.id = "crt";
    try {
      const response = await fetch(shader.file);
      if (!response.ok) throw new Error(`${shader.file}: ${response.status}`);
      const source = await response.text();

      const gl = crt.getContext("webgl", {
        alpha: false,
        antialias: false,
        depth: false,
      });
      if (!gl) throw new Error("no WebGL");
      const program = link(gl, source);
      gl.useProgram(program);

      // one triangle that covers the whole canvas
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
      gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([-1, -1, 3, -1, -1, 3]),
        gl.STATIC_DRAW,
      );
      const position = gl.getAttribLocation(program, "position");
      gl.enableVertexAttribArray(position);
      gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

      // the shader filters between the game's pixels itself, with the help of linear sampling
      gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); // y up, as in the shader

      const uniform = (name) => gl.getUniformLocation(program, name);
      const texture_size = uniform("TextureSize");
      const output_size = uniform("OutputSize");
      const frame_count = uniform("FrameCount"); // only crt-geom.glsl has it, for the interlacing
      const setting_uniforms = Object.entries(shader.uniforms).map(
        ([setting, name]) => [setting, uniform(name)],
      );
      gl.uniform1i(uniform("Texture"), 0);

      const settings = shader.settings;
      let frames = 0;
      let request = 0; // the pending animation frame, 0 if none
      function frame() {
        request = 0;
        if (window.madlove_page.active) request = requestAnimationFrame(frame);
        // the screen's size in device pixels, so the shader knows how much detail fits
        const width = Math.round(crt.clientWidth * devicePixelRatio);
        const height = Math.round(crt.clientHeight * devicePixelRatio);
        const resized = width !== crt.width || height !== crt.height;
        if (resized) {
          crt.width = width;
          crt.height = height;
          gl.viewport(0, 0, width, height);
        } else if (!game_drew) {
          return; // the canvas keeps showing the last picture
        }
        game_drew = false;
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, game);
        gl.uniform2f(texture_size, game.width, game.height);
        gl.uniform2f(output_size, width, height);
        gl.uniform1f(frame_count, frames);
        frames = (frames + 1) % 2; // the interlacing only needs to know odd from even
        for (const [setting, location] of setting_uniforms)
          gl.uniform1f(location, settings[setting]);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }

      window.madlove_crt.pause = () => {
        cancelAnimationFrame(request);
        request = 0;
      };
      window.madlove_crt.resume = () => {
        if (!request) request = requestAnimationFrame(frame);
      };

      game.parentElement.appendChild(crt);
      if (window.madlove_page.active) window.madlove_crt.resume();
    } catch (error) {
      // the game's own canvas stays visible
      console.warn("CRT effect off:", error);
      crt.remove();
    }
  }

  window.madlove_crt.start = start;
})();
