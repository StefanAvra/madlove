/*
   CRT-Geom replica by DariusG 2024-2026.
   This shader should run well on gpu's with around 100 gflops.

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

   MadLove, 2026: taken from libretro/glsl-shaders (crt/shaders/crt-geom-mini.glsl, commit 42fa8a9)
   and changed for the browser version's page, which compiles it in web/static/crt.js, with ?crt=geom.
   Only the fragment shader, in GLSL ES 1.00 for WebGL. The cabinet's tube was turned on its side, so
   the shader works in the tube's coordinates, with the scanlines running down the screen. One
   scanline per game column: the interlacing, which draws every other column in turns, is a setting
   and off by default. The colours are made linear before the scanlines, as in the original
   CRT-Geom, so the square root at the end doesn't wash them out. The dot mask is measured in the
   game's pixels instead of the screen's, so it looks the same on every screen, and it is smooth
   instead of on/off, so it can fall between the screen's pixels. The scanlines and the mask fade
   out where there are too few pixels to draw them.
*/

#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif

uniform sampler2D Texture;
uniform vec2 TextureSize;       // the game's picture, 480 x 640
uniform vec2 OutputSize;        // this canvas, in device pixels
uniform float FrameCount;       // counts the frames, for the interlacing
uniform float curve_amount;     // 0.15 in the original
uniform float cornersize;       // 0.05 in the original
uniform float DOTMASK;          // 0.3 in the original
uniform float MASK_PITCH;       // the dot mask's magenta and green pairs per row of the game's pixels
uniform float scanline_weight;  // 0.3 in the original
uniform float interlace_detect; // 1.0 in the original: in turns, every other game column

varying vec2 uv;  // 0 to 1 across the screen, y up

// the tube's (x, y) is the screen's (y, x)
#define TEX2D(c) (texture2D(Texture, (c).yx))

// Warp logic for consistency with the new corner trick
vec2 simple_warp(vec2 pos)
{
    pos = pos * 2.0 - 1.0;
    pos *= vec2(1.0 + (pos.y * pos.y) * (curve_amount * 0.2),
                1.0 + (pos.x * pos.x) * (curve_amount * 0.3));
    return pos * 0.5 + 0.5;
}

float beamWidth(vec4 color)
{
    return 0.3 + 0.1 * dot(color.rgb, vec3(0.3, 0.6, 0.1));
}

vec4 scanlineWeights(float distance, vec4 color)
{

    float wid = beamWidth(color);
    float w = distance / wid;
    return vec4((0.1 + scanline_weight) * exp(-w * w) / wid);
}

// how bright a line of this colour looks on average, through the gamma at the end, compared with
// its beam's strength: fitted to the mean of sqrt(beam) across the line for beam widths 0.3 to 0.4
float flatWeight(vec4 color)
{
    float t = beamWidth(color) - 0.3;
    return (0.1 + scanline_weight) * (1.602 + 2.13 * t - 8.2 * t * t);
}

void main()
{
    // the tube is on its side: from here on x runs along the scanlines and y across them, as in
    // the original, and the game's columns are the scanlines
    vec2 size     = TextureSize.yx;
    vec2 out_size = OutputSize.yx;

    // with interlacing, a field is every other column, and the fields take turns
    vec2 ilfac = vec2(1.0, interlace_detect > 0.5 ? 2.0 : 1.0);
    vec2 ilvec = vec2(0.0, interlace_detect > 0.5 ? mod(FrameCount, 2.0) : 0.0);
    vec2 one   = ilfac / size;

    // Geometry logic with Corner Trick
    vec2 xy = simple_warp(uv.yx);
    vec2 tube = xy;

    // --- CORNER TRICK START ---
    vec2 corn = min(xy, 1.0 - xy);
    corn.x = (cornersize * 0.001) / corn.x; // Use reciprocal for hyperbolic curve
    // --- CORNER TRICK END ---

    // Hard boundary check
    if (xy.y < 0.0 || xy.y > 1.0 || xy.x < 0.0 || xy.x > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec2 ratio_scale = (xy * size - vec2(0.5) + ilvec) / ilfac;
    vec2 uv_ratio = fract(ratio_scale);
    xy = (floor(ratio_scale) * ilfac + vec2(0.5) - ilvec) / size;

    // Catmull Filtering
    float FF = uv_ratio.x * uv_ratio.x;
    vec4 lobes = vec4(FF * uv_ratio.x, FF, uv_ratio.x, 1.0);
    vec4 InvX;
    InvX.x = dot(vec4(-0.5, 1.0, -0.5, 0.0), lobes);
    InvX.y = dot(vec4( 1.5,-2.5,  0.0, 1.0), lobes);
    InvX.z = dot(vec4(-1.5, 2.0,  0.5, 0.0), lobes);
    InvX.w = dot(vec4( 0.5,-0.5,  0.0, 0.0), lobes);

    vec4 col  = mat4(TEX2D(xy + vec2(-one.x, 0.0)),
                     TEX2D(xy),
                     TEX2D(xy + vec2(one.x, 0.0)),
                     TEX2D(xy + vec2(2.0 * one.x, 0.0))) * InvX;

    vec4 col2 = mat4(TEX2D(xy + vec2(-one.x, one.y)),
                     TEX2D(xy + vec2(0.0, one.y)),
                     TEX2D(xy + one),
                     TEX2D(xy + vec2(2.0 * one.x, one.y))) * InvX;

    col  = clamp(col, 0.0, 1.0);
    col2 = clamp(col2, 0.0, 1.0);
    vec4 weights  = scanlineWeights(uv_ratio.y, col);
    vec4 weights2 = scanlineWeights(1.0 - uv_ratio.y, col2);
    // without scanlines, the lines blend into each other, looking as bright as the beams on average
    float flat1 = flatWeight(col);
    float flat2 = flatWeight(col2);

    // linear light, as in the original CRT-Geom
    col  *= col;
    col2 *= col2;

    vec3 res = (col * weights + col2 * weights2).rgb;
    vec3 flat_res = mix(col.rgb * flat1, col2.rgb * flat2, uv_ratio.y);

    // the mask's magenta and green stripes cross the scanlines and curve with the tube; with one
    // pair per row, the middles of the game's rows are magenta. below about two of the screen's
    // pixels per pair, the stripes fade into their average, so the brightness stays the same
    float mask_room = smoothstep(1.5, 3.0, out_size.x / (size.x * MASK_PITCH));
    float green = 0.5 + 0.5 * cos(6.28318531 * tube.x * size.x * MASK_PITCH);
    vec3 dotMask = mix(vec3(1.0, 1.0 - DOTMASK, 1.0),
                       vec3(1.0 - DOTMASK, 1.0, 1.0 - DOTMASK),
                       green);
    dotMask = mix(vec3(1.0 - 0.5 * DOTMASK), dotMask, mask_room);
    res *= dotMask;
    flat_res *= dotMask;

    // below about two of the screen's pixels per line, the scanlines would beat against those
    // pixels: fade them out, after the gamma, so the brightness stays the same
    float room = smoothstep(1.5, 3.0, out_size.y / (size.y / ilfac.y));
    res = mix(sqrt(clamp(flat_res, 0.0, 1.0)), sqrt(clamp(res, 0.0, 1.0)), room);
    // Apply corner mask (if corn.y is less than the reciprocal x, black out)
    if (corn.y <= corn.x || corn.x < 0.00001) res = vec3(0.0);

    gl_FragColor = vec4(res, 1.0);
}
