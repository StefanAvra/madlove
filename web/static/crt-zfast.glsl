/*
    zfast_crt_geo - A simple, fast CRT shader.

    Copyright (C) 2017 Greg Hogan (SoltanGris42)
    Copyright (C) 2023 Jose Linares (Dogway)

    This program is free software; you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the Free
    Software Foundation; either version 2 of the License, or (at your option)
    any later version.


Notes:  This shader does scaling with a weighted linear filter
        based on the algorithm by Iñigo Quilez here:
        https://iquilezles.org/articles/texture/
        but modified to be somewhat sharper. Then a scanline effect that varies
        based on pixel brightness is applied along with a monochrome aperture mask.
        This shader runs at ~60fps on the Chromecast HD (10GFlops) on a 1080p display.
        (https://forums.libretro.com/t/android-googletv-compatible-shaders-nitpicky)

Dogway: I modified zfast_crt.glsl shader to include screen curvature,
        vignetting, round corners and phosphor*temperature. Horizontal pixel is left out
        from the Quilez' algo (read above) to provide a more S-Video like horizontal blur.
        The scanlines and mask are also now performed in the recommended linear light.
        For this to run smoothly on GPU deprived platforms like the Chromecast and
        older consoles, I had to remove several parameters and hardcode them into the shader.
        Another POV is to run the shader on handhelds like the Switch or SteamDeck so they consume less battery.

MadLove, 2026: taken from libretro/glsl-shaders (crt/shaders/zfast_crt_geo.glsl, commit c6c8fad) and
        changed for the browser version's page, which compiles it in web/static/crt.js. Only the
        fragment shader, in GLSL ES 1.00 for WebGL. The cabinet's tube was turned on its side, so the
        shader works in the tube's coordinates, with the scanlines running down the screen. The mask
        is measured in the game's pixels, as the scanlines are, instead of the screen's, so it looks
        the same on every screen; it is smooth instead of on/off, so it can fall between the screen's
        pixels. The scanlines and the mask fade out where there are too few pixels to draw them. The
        curvature, the vignette and the colour temperature can be changed.
*/

#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif

uniform sampler2D Texture;
uniform vec2 TextureSize;        // the game's picture, 480 x 640
uniform vec2 OutputSize;         // this canvas, in device pixels
uniform float SCANLINE_WEIGHT;   // 7.0 in the original
uniform float MASK_DARK;         // 0.5 in the original
uniform float MASK_PITCH;        // the mask's stripes per row of the game's pixels
uniform float CURVE;             // 1.0: the original's curvature
uniform float VIGNETTE;          // 1.0: the original's vignette, 0.0: none
uniform float D93;               // 1.0: the original's colour temperature, 0.0: the game's colours

varying vec2 uv;  // 0 to 1 across the screen, y up

// NTSC-J (D93) -> Rec709 D65 Joint Matrix (with D93 simulation)
// This is compensated for a linearization hack (RGB*RGB and then sqrt())
const mat3 P22D93 = mat3(
     1.00000, 0.00000, -0.06173,
     0.07111, 0.96887, -0.01136,
     0.00000, 0.08197,  1.07280);


// Returns gamma corrected output, compensated for scanline+mask embedded gamma
vec3 inv_gamma(vec3 col, vec3 power)
{
    vec3 cir  = col-1.0;
         cir *= cir;
         col  = mix(sqrt(col),sqrt(1.0-cir),power);
    return col;
}

vec2 Warp(vec2 pos)
{
    pos  = pos*2.0-1.0;
    pos *= vec2(1.0 + (pos.y*pos.y)*0.0276*CURVE, 1.0 + (pos.x*pos.x)*0.0414*CURVE);
    return pos*0.5 + 0.5;
}


void main()
{
    // the tube is on its side: from here on x runs along the scanlines and y across them, as in
    // the original, and the game's columns are the scanlines
    vec2 vpos     = uv.yx;
    vec2 size     = TextureSize.yx;
    vec2 out_size = OutputSize.yx;

    vec2 xy     = Warp(vpos);

    vec2 corn   = min(xy,1.0-xy); // This is used to mask the rounded
         corn.x = 0.0001/corn.x;  // corners later on

          vpos *= (1.0 - vpos.xy);
    float vig   = vpos.x * vpos.y * 46.0;
          vig   = min(sqrt(vig), 1.0);
          vig   = max(mix(1.0, vig, VIGNETTE), 0.0);


    // Of all the pixels that are mapped onto the texel we are
    // currently rendering, which pixel are we currently rendering?
    float ratio_scale = xy.y * size.y - 0.5;
    // Snap to the center of the underlying texel.
    float i = floor(ratio_scale) + 0.5;

    // This is just like "Quilez Scaling" but sharper
    float f = ratio_scale - i;
    float Y = f*f;
    float p = (i + 4.0*Y*f)/size.y;

    // below about two of the screen's pixels per line or stripe, the scanlines and the mask would
    // beat against those pixels: fade them out
    float room      = smoothstep(1.5, 3.0, out_size.y/size.y);
    float weight    = SCANLINE_WEIGHT*room;
    float mask_room = smoothstep(1.5, 3.0, out_size.x/(size.x*MASK_PITCH));
    float mask_dark = MASK_DARK*mask_room;

    // This compensates the scanline+mask embedded gamma from the beam dynamics
    vec3 pwr = vec3(1.0/((-0.0325*weight+1.0)*(-0.311*mask_dark+1.0))-1.2);

    // the mask's stripes cross the scanlines and curve with the tube. each stripe is brightest
    // in its middle; with one stripe per row, the middles are the middles of the game's rows
    float stripe = xy.x*size.x*MASK_PITCH;
    float mask   = 1.0 - mask_dark*(0.5 + 0.5*cos(6.28318531*stripe));
    // the tube's (x, y) is the screen's (y, x)
    vec3 colour = texture2D(Texture, vec2(p,xy.x)).rgb;

    colour = colour*colour;
    colour = max(mix(colour, colour*P22D93, D93) * vig, 0.0);

    float scanLineWeight = mix(1.0, 1.5 - SCANLINE_WEIGHT*(Y - Y*Y), room);

    if (corn.y <= corn.x || corn.x < 0.0001 )
    colour = vec3(0.0);

    gl_FragColor = vec4(inv_gamma(colour.rgb*mix(scanLineWeight*mask, 1.0, colour.r*0.26667+colour.g*0.26667+colour.b*0.26667),pwr),1.0);

}
