"""OpenGL (moderngl) renderer for the New York world: terrain, water, sky, instanced props with
growth over time, sun shadows, particles and a tilt-shift post pass with a 2D overlay."""
import math

import moderngl
import numpy as np

import meshes
from world import CELL, NX, NZ, WATER_Y, X0, Z0

W, H = 1280, 720
SHADOW = 2048


# ------------------------------------------------------------------ math
def perspective(fovy, aspect, near, far):
    f = 1 / math.tan(math.radians(fovy) / 2)
    m = np.zeros((4, 4), np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = 2 * far * near / (near - far)
    m[3, 2] = -1
    return m


def ortho(hw, hh, near, far):
    m = np.eye(4, dtype=np.float32)
    m[0, 0] = 1 / hw
    m[1, 1] = 1 / hh
    m[2, 2] = -2 / (far - near)
    m[2, 3] = -(far + near) / (far - near)
    return m


def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(lambda a: np.asarray(a, np.float32), (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.eye(4, dtype=np.float32)
    m[0, :3], m[1, :3], m[2, :3] = s, u, -f
    m[0, 3], m[1, 3], m[2, 3] = -s @ eye, -u @ eye, f @ eye
    return m


def gl(m):
    return np.ascontiguousarray(m.T, dtype=np.float32).tobytes()


# ------------------------------------------------------------------ shaders
COMMON = """
uniform vec3 camPos; uniform vec3 sunDir; uniform vec3 sunCol; uniform vec3 skyCol; uniform vec3 groundCol;
uniform vec3 fogCol; uniform float fogDen; uniform mat4 lightVP; uniform sampler2DShadow shadowMap;
uniform float night; uniform float year; uniform float time;
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(hash(i),hash(i+vec2(1,0)),f.x), mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x), f.y); }
float shadowF(vec3 wp){ vec4 lp = lightVP*vec4(wp,1.); vec3 p = lp.xyz/lp.w*0.5+0.5;
  if(p.x<0.||p.x>1.||p.y<0.||p.y>1.||p.z>1.) return 1.;
  float s=0.; float ts = 1.0/2048.0;
  for(int i=-1;i<=1;i++) for(int j=-1;j<=1;j++) s += texture(shadowMap, vec3(p.xy+vec2(i,j)*ts*1.3, p.z-0.0012));
  return s/9.; }
vec3 fogit(vec3 c, vec3 wp){ float d=length(wp-camPos); float f=1.-exp(-pow(d*fogDen,1.35)); return mix(c,fogCol,clamp(f,0.,1.)); }
vec3 shade(vec3 base, vec3 n, vec3 wp, float sh){
  float d = max(dot(n, sunDir), 0.) * sh;
  float hemi = 0.5 + 0.5*n.y;
  vec3 amb = mix(groundCol, skyCol, hemi);
  return base*(amb + sunCol*d);
}
"""

INST_VS = """
#version 330
in vec3 vpos; in vec3 vnrm; in float vpart;
in vec3 ipos; in vec3 iscl; in float irot; in vec3 icol; in vec3 icol2; in float ibirth; in float ideath; in float ivar; in vec4 imove;
uniform mat4 VP; uniform float year; uniform float time; uniform float growDur; uniform float bob; uniform float worldMesh;
out vec3 wpos; out vec3 nrm; out vec3 col; out vec3 col2; out float part; out vec3 lpos; out float var_; out vec3 iscale;
void main(){
  float g = clamp((year-ibirth)/growDur, 0., 1.); g = g*g*(3.-2.*g);
  float d = 1. - clamp((year-ideath)/0.35, 0., 1.);
  float k = g*d;
  if(k < 0.003){ gl_Position = vec4(0., 0., 2., 1.); return; }
  vec3 p = vpos;
  float a = irot;
  vec2 mv = vec2(0.);
  if(imove.w > imove.z){ mv = imove.xy * smoothstep(imove.z, imove.w, year); if(length(imove.xy)>0.) a = atan(imove.x, imove.y); }
  if(vpart > 3.5 && vpart < 4.5){ vec2 q = p.xy - vec2(0., 1.02); float an = time*1.4 + ivar*6.;
     p.xy = vec2(q.x*cos(an)-q.y*sin(an), q.x*sin(an)+q.y*cos(an)) + vec2(0., 1.02); }
  vec3 s = worldMesh > 0.5 ? vec3(1., k, 1.) : iscl*vec3(mix(0.8,1.,k), k, mix(0.8,1.,k));
  lpos = vpos*iscl;
  p *= s;
  if(vpart > 2.5 && vpart < 3.5) p.x += sin(time*7. + p.z*0.4 + ivar*9.) * 0.08 * max(iscl.x, 1.);
  vec3 r = vec3(p.x*cos(a) + p.z*sin(a), p.y, -p.x*sin(a) + p.z*cos(a));
  vec3 n = vec3(vnrm.x*cos(a) + vnrm.z*sin(a), vnrm.y, -vnrm.x*sin(a) + vnrm.z*cos(a));
  wpos = ipos + vec3(mv.x, 0., mv.y) + r;
  if(bob > 0.){ wpos.y += sin(time*1.3 + ivar*40.)*0.3*bob; }
  nrm = n; col = icol; col2 = icol2; part = vpart; var_ = ivar; iscale = iscl;
  gl_Position = VP*vec4(wpos, 1.);
}
"""

INST_FS = """
#version 330
in vec3 wpos; in vec3 nrm; in vec3 col; in vec3 col2; in float part; in vec3 lpos; in float var_; in vec3 iscale;
uniform float windows; uniform float shipMode; uniform vec3 flagCol; uniform float flagFromInst;
out vec4 frag;
""" + COMMON + """
void main(){
  vec3 n = normalize(nrm);
  vec3 base;
  if(part < 0.5) base = col;
  else if(part < 1.5) base = shipMode > 0.5 ? vec3(0.45,0.33,0.22) : col2;
  else if(part < 2.5) base = vec3(0.93, 0.91, 0.86);
  else if(part < 3.5) base = flagFromInst > 0.5 ? col2 : flagCol;
  else if(part < 4.5) base = vec3(0.86, 0.82, 0.72);
  else base = vec3(0.26, 0.20, 0.15);
  vec3 emis = vec3(0.);
  if(windows > 0.5 && part < 0.5 && abs(n.y) < 0.3){
    float u = abs(n.x) > abs(n.z) ? lpos.z : lpos.x;
    float v = lpos.y;
    float fh = windows > 1.5 ? 3.9 : 3.0;
    float cw = windows > 1.5 ? 3.2 : 2.6;
    float fu = fract(u/cw), fv = fract(v/fh);
    float top = iscale.y;
    float win = step(0.22, fu)*step(fu, 0.78)*step(0.28, fv)*step(fv, 0.82)*step(1.2, v)*step(v, top-0.8);
    vec2 cell = vec2(floor(u/cw), floor(v/fh));
    if(windows > 1.5){
      vec3 glass = mix(base*0.55, skyCol*0.9, 0.35 + 0.25*hash(cell+var_));
      base = mix(base, glass, win*0.85);
    } else {
      base = mix(base, vec3(0.16, 0.18, 0.22), win*0.8);
    }
    float lit = step(hash(cell*1.7 + var_*13.), 0.55);
    emis = win*lit*night*vec3(1.0, 0.78, 0.48)*1.35;
  }
  if(part > 1.5 && part < 2.5 && shipMode < 0.5 && windows < 0.5) emis += night*vec3(1.,0.85,0.5)*0.6;
  float sh = shadowF(wpos + n*0.4);
  vec3 c = shade(base, n, wpos, sh) + emis;
  frag = vec4(fogit(c, wpos), 1.);
}
"""

SHADOW_FS = """
#version 330
void main(){}
"""

TERRAIN_VS = """
#version 330
in vec2 xz; in vec3 hab; in vec3 nA; in vec3 nB; in vec2 wetw; in vec4 land; in vec2 extra;
uniform mat4 VP; uniform float year;
out vec3 wpos; out vec3 nrm; out float wet; out vec4 lu; out vec2 ex; out float h0;
void main(){
  float f = smoothstep(hab.z-3., hab.z, year);
  float hl = mix(hab.x, hab.y, f);
  float w = smoothstep(wetw.x-3., wetw.x, year) * (1. - smoothstep(wetw.y-3., wetw.y+0.5, year));
  float y = mix(hl, """ + str(WATER_Y) + """, w);
  wpos = vec3(xz.x, y, xz.y); nrm = normalize(mix(mix(nA, nB, f), vec3(0,1,0), w)); wet = w; lu = land; ex = extra; h0 = hl;
  gl_Position = VP*vec4(wpos, 1.);
}
"""

TERRAIN_FS = """
#version 330
in vec3 wpos; in vec3 nrm; in float wet; in vec4 lu; in vec2 ex; in float h0;
uniform sampler2D roadTex; uniform vec4 roadRect;
out vec4 frag;
""" + COMMON + """
void main(){
  vec2 p = wpos.xz;
  float n1 = vnoise(p/35.), n2 = vnoise(p/9.), n3 = vnoise(p/180.);
  vec3 grass = mix(vec3(0.30,0.52,0.18), vec3(0.45,0.62,0.24), n1*0.7+n3*0.3);
  vec3 c = grass;
  float forest = lu.w * (1. - smoothstep(lu.x-4., lu.x+2., year));
  float bl = vnoise(p/6.)*0.5 + vnoise(p/14.)*0.5;
  vec3 canopy = mix(vec3(0.08,0.20,0.08), vec3(0.24,0.42,0.16), bl*0.8 + n1*0.2);
  c = mix(c, canopy, forest);
  if(ex.x > 0.35 && year < 1660.) c = mix(c, mix(vec3(0.58,0.52,0.30), vec3(0.46,0.50,0.26), step(0.5, fract(p.x/7.))), 0.85);
  float farm = step(lu.y, year) * (1. - step(lu.z, year));
  if(farm > 0.5 && forest < 0.5){
    vec2 cell = floor(p/vec2(140., 95.) + vec2(n3*0.6, 0.));
    float hv = hash(cell);
    vec3 fc = hv < 0.33 ? vec3(0.62,0.60,0.32) : (hv < 0.66 ? vec3(0.42,0.56,0.24) : vec3(0.52,0.50,0.30));
    float rows = 0.92 + 0.08*step(0.5, fract(dot(p, hv < 0.5 ? vec2(1.,0.) : vec2(0.,1.))/5.));
    vec2 e = fract(p/vec2(140., 95.) + vec2(n3*0.6, 0.));
    float hedge = 1. - step(0.03, e.x)*step(e.x, 0.97)*step(0.04, e.y)*step(e.y, 0.96);
    fc = mix(fc*rows, vec3(0.20,0.32,0.15), hedge);
    c = mix(c, fc, 0.85);
  }
  float urb = step(lu.z, year);
  if(urb > 0.5){
    vec3 garden = mix(vec3(0.36,0.50,0.22), vec3(0.50,0.52,0.30), step(0.5, hash(floor(p/vec2(18.,24.)))));
    vec3 dirt = mix(vec3(0.56,0.50,0.42), vec3(0.50,0.45,0.38), n2);
    float gardens = 1. - smoothstep(1720., 1840., year);
    vec3 ground = year < 1900. ? mix(dirt, garden, gardens*0.75) : mix(vec3(0.44,0.44,0.45), vec3(0.38,0.38,0.40), n2);
    c = ground;
    if(ex.y < 0.5 && (p.x < -560. || p.x > 2300. || p.y > 300. || p.y < -9000. || abs(p.x) > 2500.)){
      vec2 g = fract(p/vec2(60.,90.)); float blk = step(0.12,g.x)*step(0.1,g.y);
      vec3 roofs = mix(vec3(0.55,0.42,0.36), vec3(0.62,0.6,0.58), hash(floor(p/vec2(14.,14.))));
      c = mix(vec3(0.35,0.35,0.37), roofs, blk);
      c += night*blk*step(0.7, hash(floor(p/vec2(7.,7.))))*vec3(0.9,0.7,0.4)*0.6;
    }
  }
  if(ex.y > 0.5) c = mix(vec3(0.33,0.50,0.24), vec3(0.40,0.56,0.27), n1);
  vec2 ruv = (p - roadRect.xy)/roadRect.zw;
  if(ruv.x>0. && ruv.x<1. && ruv.y>0. && ruv.y<1. && wet < 0.5){
    float ry = texture(roadTex, ruv).r;
    if(year >= ry){
      vec3 rc = year < 1700. ? vec3(0.64,0.54,0.40) : (year < 1900. ? vec3(0.58,0.55,0.50) : vec3(0.27,0.27,0.29));
      c = mix(rc, rc*0.9, n2);
    }
  }
  float sand = (1. - smoothstep(1.2, 3.2, h0)) * (1. - wet);
  c = mix(c, vec3(0.80,0.74,0.58), sand*(urb > 0.5 ? 0.2 : 0.9));
  if(wet > 0.5) c = vec3(0.45,0.42,0.33);
  float sh = shadowF(wpos + vec3(0., 0.3, 0.));
  vec3 col = shade(c, normalize(nrm), wpos, sh);
  frag = vec4(fogit(col, wpos), 1.);
}
"""

WATER_VS = """
#version 330
in vec2 xz; uniform mat4 VP; out vec3 wpos;
void main(){ wpos = vec3(xz.x, 0., xz.y); gl_Position = VP*vec4(wpos, 1.); }
"""

WATER_FS = """
#version 330
in vec3 wpos; uniform sampler2D hTex; uniform sampler2D wTex; uniform vec4 hRect; uniform vec3 skyTop; uniform vec3 skyHor;
out vec4 frag;
""" + COMMON + """
void main(){
  vec2 p = wpos.xz;
  vec2 uv = (p - hRect.xy)/hRect.zw;
  float depth = 30.;
  if(uv.x>0. && uv.x<1. && uv.y>0. && uv.y<1.){
    vec3 h = texture(hTex, uv).rgb;
    vec2 ww = texture(wTex, uv).rg;
    float hl = mix(h.r, h.g, smoothstep(h.b-3., h.b, year));
    float w = smoothstep(ww.x-3., ww.x, year) * (1. - smoothstep(ww.y-3., ww.y+0.5, year));
    float ty = mix(hl, """ + str(WATER_Y) + """, w);
    if(ty > 0.15) discard;
    depth = -ty;
  }
  float t = time;
  vec2 g = vec2(0.);
  g += vec2(cos(p.x*0.06 + t*1.1), cos(p.y*0.07 + t*0.9))*0.06;
  g += vec2(cos(p.x*0.21 + p.y*0.13 + t*2.0), cos(p.y*0.19 - p.x*0.11 + t*1.7))*0.035;
  g += (vec2(vnoise(p*0.05 + t*0.2), vnoise(p*0.05 - t*0.2)) - 0.5)*0.08;
  vec3 n = normalize(vec3(g.x, 1., g.y));
  vec3 V = normalize(camPos - wpos);
  float fres = pow(1. - max(dot(V, n), 0.), 4.);
  vec3 deep = vec3(0.04, 0.26, 0.50), shallow = vec3(0.10, 0.55, 0.62);
  vec3 wc = mix(shallow, deep, smoothstep(0.5, 8., depth));
  wc = shade(wc, vec3(0,1,0), wpos, 1.0);
  vec3 refl = mix(skyHor, skyTop, 0.35);
  vec3 c = mix(wc, refl, 0.15 + 0.55*fres);
  vec3 Rv = reflect(-sunDir, n);
  c += sunCol * pow(max(dot(Rv, V), 0.), 160.) * 0.9;
  float foam = (1. - smoothstep(0.2, 1.6, depth)) * (0.6 + 0.4*sin(depth*6. - t*2.5));
  c = mix(c, vec3(0.92,0.95,0.95), clamp(foam, 0., 1.)*0.55);
  frag = vec4(fogit(c, wpos), 1.);
}
"""

SKY_VS = """
#version 330
in vec2 q; out vec2 uv; void main(){ uv = q; gl_Position = vec4(q, 0.9999, 1.); }
"""
SKY_FS = """
#version 330
in vec2 uv; uniform mat4 invVP; uniform vec3 skyTop; uniform vec3 skyHor; uniform vec3 sunDir; uniform vec3 sunCol;
uniform float night; uniform vec3 fogCol;
out vec4 frag;
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void main(){
  vec4 a = invVP*vec4(uv, -1., 1.); vec4 b = invVP*vec4(uv, 1., 1.);
  vec3 d = normalize(b.xyz/b.w - a.xyz/a.w);
  float h = clamp(d.y, 0., 1.);
  vec3 c = mix(skyHor, skyTop, pow(h, 0.55));
  float s = max(dot(d, sunDir), 0.);
  c += sunCol*(pow(s, 900.)*3. + pow(s, 12.)*0.25);
  if(night > 0.05){ vec2 st = floor(d.xz/max(d.y,0.05)*300.); float star = step(0.9985, hash(st)); c += star*night*h*0.9; }
  if(d.y < 0.) c = fogCol;
  frag = vec4(c, 1.);
}
"""

PART_VS = """
#version 330
in vec2 q; in vec3 ic; in float isz; in vec4 icol; uniform mat4 VP; uniform vec3 camR; uniform vec3 camU;
out vec2 uv; out vec4 col; out vec3 wpos;
void main(){ uv = q; col = icol; wpos = ic + (camR*q.x + camU*q.y)*isz; gl_Position = VP*vec4(wpos, 1.); }
"""
PART_FS = """
#version 330
in vec2 uv; in vec4 col; in vec3 wpos; uniform vec3 camPos; uniform vec3 fogCol; uniform float fogDen;
out vec4 frag;
void main(){ float r = length(uv); if(r > 1.) discard; float a = col.a*(1. - smoothstep(0.3, 1., r));
  float d = length(wpos-camPos); float f = 1.-exp(-pow(d*fogDen,1.35));
  frag = vec4(mix(col.rgb, fogCol, f*0.7), a); }
"""

POST_VS = """
#version 330
in vec2 q; out vec2 uv; void main(){ uv = q*0.5+0.5; gl_Position = vec4(q, 0., 1.); }
"""
POST_FS = """
#version 330
in vec2 uv; uniform sampler2D scene; uniform sampler2D overlay; uniform float tilt; uniform vec2 texel;
uniform float fade; uniform vec3 grade;
out vec4 frag;
void main(){
  vec3 c = texture(scene, uv).rgb;
  float b = (smoothstep(0.62, 1.0, uv.y)*1.0 + smoothstep(0.22, 0.0, uv.y)*0.6) * tilt;
  if(b > 0.02){
    vec3 acc = c; float wsum = 1.;
    for(int i=0;i<12;i++){ float a = float(i)*2.39996; float r = sqrt(float(i)+0.5)/3.5;
      vec2 o = vec2(cos(a), sin(a))*r*b*7.*texel; acc += texture(scene, uv+o).rgb; wsum += 1.; }
    c = acc/wsum;
  }
  float l = dot(c, vec3(0.299,0.587,0.114));
  c = mix(vec3(l), c, 1.22);
  c *= grade;
  c = pow(max(c, 0.), vec3(0.97));
  vec2 v = uv - 0.5; c *= 1. - dot(v, v)*0.55;
  vec4 o = texture(overlay, vec2(uv.x, 1.-uv.y)).bgra;
  c = c*(1.-o.a) + o.rgb;
  c *= fade;
  frag = vec4(c, 1.);
}
"""

INST_FIELDS = 21


def inst_array(lst):
    a = np.zeros((len(lst), INST_FIELDS), np.float32)
    for i, d in enumerate(lst):
        a[i, 0:3] = d["pos"]
        a[i, 3:6] = d["scale"]
        a[i, 6] = d["rot"]
        a[i, 7:10] = d["col"]
        a[i, 10:13] = d["col2"]
        a[i, 13] = d["birth"]
        a[i, 14] = d["death"]
        a[i, 15] = d["var"]
        a[i, 16:20] = d["move"]
    return a


GROUPS = {  # kind: (mesh, growDur, bob, windows, shipMode, castShadow, maxdist)
    "house": ("house", 1.2, 0, 1, 0, 1, 6500), "row": ("row", 1.5, 0, 1, 0, 1, 7500),
    "tower": ("tower", 3.0, 0, 2, 0, 1, 30000), "spire": ("spire", 2.0, 0, 0, 0, 1, 30000),
    "tree": ("tree", 3.0, 0, 0, 0, 1, 4500), "pine": ("pine", 3.0, 0, 0, 0, 1, 4500),
    "longhouse": ("longhouse", 0.5, 0, 0, 0, 1, 6000), "canoe": ("canoe", 0.2, 0.3, 0, 0, 0, 3000),
    "windmill": ("windmill", 1.0, 0, 0, 0, 1, 8000), "church": ("church", 2.0, 0, 0, 0, 1, 12000),
    "palisade": ("palisade", 0.4, 0, 0, 0, 1, 5000), "pier": ("pier", 2.0, 0, 0, 0, 1, 8000),
    "ship": ("ship", 0.15, 1, 0, 1, 1, 12000), "steamer": ("steamer", 0.3, 1, 0, 1, 1, 12000),
}


class Renderer:
    def __init__(self, world):
        self.w = world
        self.ctx = moderngl.create_standalone_context()
        ctx = self.ctx
        self.msaa = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4, samples=4)],
                                    depth_attachment=ctx.depth_renderbuffer((W, H), samples=4))
        self.scene_tex = ctx.texture((W, H), 4)
        self.scene_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.scene_tex.repeat_x = self.scene_tex.repeat_y = False
        self.resolve = ctx.framebuffer(color_attachments=[self.scene_tex])
        self.out_tex = ctx.texture((W, H), 3)
        self.out_fbo = ctx.framebuffer(color_attachments=[self.out_tex])
        self.shadow_tex = ctx.depth_texture((SHADOW, SHADOW))
        self.shadow_tex.compare_func = "<="
        self.shadow_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.shadow_fbo = ctx.framebuffer(depth_attachment=self.shadow_tex)
        self.overlay_tex = ctx.texture((W, H), 4)
        self.p_inst = ctx.program(vertex_shader=INST_VS, fragment_shader=INST_FS)
        self.p_inst_sh = ctx.program(vertex_shader=INST_VS, fragment_shader=SHADOW_FS)
        self.p_ter = ctx.program(vertex_shader=TERRAIN_VS, fragment_shader=TERRAIN_FS)
        self.p_wat = ctx.program(vertex_shader=WATER_VS, fragment_shader=WATER_FS)
        self.p_sky = ctx.program(vertex_shader=SKY_VS, fragment_shader=SKY_FS)
        self.p_part = ctx.program(vertex_shader=PART_VS, fragment_shader=PART_FS)
        self.p_post = ctx.program(vertex_shader=POST_VS, fragment_shader=POST_FS)
        quad = np.array([-1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1], np.float32)
        self.quad_buf = ctx.buffer(quad.tobytes())
        self.vao_sky = ctx.vertex_array(self.p_sky, [(self.quad_buf, "2f", "q")])
        self.vao_post = ctx.vertex_array(self.p_post, [(self.quad_buf, "2f", "q")])
        self._terrain()
        self._water()
        self._props()
        self.part_buf = ctx.buffer(reserve=4 * 8 * 6000)
        self.vao_part = ctx.vertex_array(self.p_part, [(self.quad_buf, "2f", "q"),
                                                       (self.part_buf, "3f 1f 4f/i", "ic", "isz", "icol")])

    # ---------------------------------------------------------------- setup
    def _terrain(self):
        w = self.w

        def normals(h):
            gz, gx = np.gradient(h, CELL)
            n = np.stack([-gx, np.ones_like(h), -gz], -1)
            return n / np.linalg.norm(n, axis=-1, keepdims=True)

        clear = np.minimum(w.farm_year, w.urban_year)
        fy = np.clip(w.fill_year, -1e5, 1e5)
        data = np.concatenate([
            np.stack([w.gx, w.gz], -1), np.stack([w.h_a, w.h_b, fy], -1), normals(w.h_a), normals(w.h_b),
            np.stack([np.clip(w.wet_from, -1e5, 1e5), np.clip(w.wet_to, -1e5, 1e5)], -1),
            np.stack([clear, w.farm_year, w.urban_year, w.forest], -1),
            np.stack([w.lenape_field, w.park], -1)], -1).astype(np.float32).reshape(-1, 19)
        idx = []
        I = np.arange(NZ * NX).reshape(NZ, NX)
        a, b, c, d = I[:-1, :-1], I[:-1, 1:], I[1:, :-1], I[1:, 1:]
        idx = np.stack([a, c, b, b, c, d], -1).reshape(-1).astype(np.uint32)
        self.ter_vbo = self.ctx.buffer(data.tobytes())
        self.ter_ibo = self.ctx.buffer(idx.tobytes())
        self.vao_ter = self.ctx.vertex_array(self.p_ter, [(self.ter_vbo, "2f 3f 3f 3f 2f 4f 2f", "xz", "hab", "nA", "nB",
                                                           "wetw", "land", "extra")], self.ter_ibo)
        rt = w.road_tex.astype(np.float32)
        self.road_tex = self.ctx.texture((rt.shape[1], rt.shape[0]), 1, rt.tobytes(), dtype="f4")
        self.road_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.road_rect = (w.RX0, w.RZ0, w.RX1 - w.RX0, w.RZ1 - w.RZ0)
        ht = np.stack([w.h_a, w.h_b, fy, np.zeros_like(fy)], -1).astype(np.float32)
        self.h_tex = self.ctx.texture((NX, NZ), 4, ht.tobytes(), dtype="f4")
        self.h_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        wt = np.stack([np.clip(w.wet_from, -1e5, 1e5), np.clip(w.wet_to, -1e5, 1e5)], -1).astype(np.float32)
        self.w_tex = self.ctx.texture((NX, NZ), 2, wt.tobytes(), dtype="f4")
        self.w_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.h_rect = (X0, Z0, (NX - 1) * CELL, (NZ - 1) * CELL)

    def _water(self):
        R = 60000
        q = np.array([-R, -R, R, -R, R, R, -R, -R, R, R, -R, R], np.float32)
        # subdivide a bit for precision
        self.wat_buf = self.ctx.buffer(q.tobytes())
        self.vao_wat = self.ctx.vertex_array(self.p_wat, [(self.wat_buf, "2f", "xz")])

    def _props(self):
        ctx = self.ctx
        self.groups = []
        fmt = "3f 3f 1f 3f 3f 1f 1f 1f 4f 1x4/i"
        names = ("ipos", "iscl", "irot", "icol", "icol2", "ibirth", "ideath", "ivar", "imove")
        mesh_cache = {}

        def make(kind, mesh, lst, grow, bob, windows, ship, cast, maxd, world_mesh=0):
            if not lst:
                return
            if mesh not in mesh_cache:
                mesh_cache[mesh] = ctx.buffer(meshes.MESHES[mesh]().tobytes())
            vb = mesh_cache[mesh]
            data = inst_array(lst)
            ib = ctx.buffer(reserve=max(1, len(data)) * INST_FIELDS * 4)
            vao = ctx.vertex_array(self.p_inst, [(vb, "3f 3f 1f", "vpos", "vnrm", "vpart"), (ib, fmt, *names)])
            vao_sh = ctx.vertex_array(self.p_inst_sh, [(vb, "3f 3f 1f", "vpos", "vnrm", "vpart"), (ib, fmt, *names)])
            self.groups.append(dict(kind=kind, data=data, ib=ib, vao=vao, vao_sh=vao_sh, grow=grow, bob=bob,
                                    windows=windows, ship=ship, cast=cast, maxd=maxd, world=world_mesh, n=0,
                                    fromInst=1 if ship else 0))

        for kind, (mesh, grow, bob, win, ship, cast, maxd) in GROUPS.items():
            make(kind, mesh, self.w.I[kind], grow, bob, win, ship, cast, maxd)
        for d in self.w.I["special"]:
            make("special:" + d["mesh"], d["mesh"], [d], 2.5 if d["mesh"] != "fort" else 1.0, 0, 0, 0, 1, 40000,
                 world_mesh=1)

    # ---------------------------------------------------------------- per frame
    def _cull(self, VP, year, cam):
        for g in self.groups:
            a = g["data"]
            alive = (a[:, 13] <= year) & (a[:, 14] + 0.4 >= year)
            mov = a[:, 19] > a[:, 18]
            pos = a[:, 0:3].copy()
            if mov.any():
                f = np.clip((year - a[:, 18]) / np.maximum(a[:, 19] - a[:, 18], 1e-6), 0, 1)
                f = f * f * (3 - 2 * f)
                f = np.where(mov, f, 0)
                pos[:, 0] += a[:, 16] * f
                pos[:, 2] += a[:, 17] * f
            if not g["world"]:
                d2 = ((pos - cam) ** 2).sum(1)
                alive &= d2 < g["maxd"] ** 2
                hp = np.concatenate([pos + np.array([0, 10, 0], np.float32), np.ones((len(pos), 1), np.float32)], 1)
                cp = hp @ VP.T
                wv = cp[:, 3]
                r = np.max(a[:, 3:6], 1)
                m = 1.0 + 1.3 * r / np.maximum(wv, 1)
                ok = (wv > -r) & (np.abs(cp[:, 0]) < m * np.abs(wv) + r) & (np.abs(cp[:, 1]) < m * np.abs(wv) + r + 40)
                alive &= ok
            sel = a[alive]
            g["n"] = len(sel)
            if len(sel):
                g["ib"].write(sel.tobytes())

    def set_common(self, p, S):
        for k, v in (("camPos", S["cam"]), ("sunDir", S["sun_dir"]), ("sunCol", S["sun_col"]), ("skyCol", S["sky_amb"]),
                     ("groundCol", S["ground_amb"]), ("fogCol", S["fog_col"]), ("fogDen", S["fog_den"]),
                     ("night", S["night"]), ("year", S["year"]), ("time", S["time"])):
            if k in p:
                p[k].value = tuple(v) if hasattr(v, "__len__") else float(v)
        if "lightVP" in p:
            p["lightVP"].write(gl(self.lightVP))
        if "shadowMap" in p:
            p["shadowMap"].value = 7

    def render(self, S, overlay_bytes, particles):
        ctx = self.ctx
        cam = np.asarray(S["cam"], np.float32)
        tgt = np.asarray(S["target"], np.float32)
        V = look_at(cam, tgt)
        dist = float(np.linalg.norm(cam - tgt))
        P = perspective(S["fov"], W / H, max(2.0, dist * 0.004), 60000)
        VP = P @ V
        year = S["year"]
        # shadow camera around target
        sd = np.asarray(S["sun_dir"], np.float32)
        half = float(np.clip(dist * 0.85, 300, 3200))
        focus = tgt + (cam - tgt) * 0.15
        LV = look_at(focus + sd * 4000, focus, up=(0, 0, -1) if abs(sd[1]) > 0.99 else (0, 1, 0))
        LP = ortho(half, half, 10, 9000)
        self.lightVP = LP @ LV
        self._cull(VP, year, cam)
        # shadow pass
        self.shadow_fbo.use()
        self.shadow_fbo.clear(depth=1.0)
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        p = self.p_inst_sh
        p["VP"].write(gl(self.lightVP))
        p["year"].value = year
        if "time" in p:
            p["time"].value = S["time"]
        for g in self.groups:
            if g["n"] and g["cast"]:
                p["growDur"].value = g["grow"]
                if "bob" in p:
                    p["bob"].value = g["bob"]
                p["worldMesh"].value = g["world"]
                g["vao_sh"].render(instances=g["n"])
        # main pass
        self.msaa.use()
        ctx.viewport = (0, 0, W, H)
        self.msaa.clear(*S["fog_col"], 1.0, depth=1.0)
        self.shadow_tex.use(7)
        ctx.disable(moderngl.DEPTH_TEST)
        ps = self.p_sky
        ps["invVP"].write(gl(np.linalg.inv(VP)))
        for k in ("skyTop", "skyHor", "sunDir", "sunCol", "fogCol"):
            ps[k].value = tuple({"skyTop": S["sky_top"], "skyHor": S["sky_hor"], "sunDir": S["sun_dir"],
                                 "sunCol": S["sun_col"], "fogCol": S["fog_col"]}[k])
        ps["night"].value = S["night"]
        self.vao_sky.render()
        ctx.enable(moderngl.DEPTH_TEST)
        pt = self.p_ter
        pt["VP"].write(gl(VP))
        self.set_common(pt, S)
        self.road_tex.use(1)
        pt["roadTex"].value = 1
        pt["roadRect"].value = self.road_rect
        self.vao_ter.render()
        pi = self.p_inst
        pi["VP"].write(gl(VP))
        self.set_common(pi, S)
        pi["flagCol"].value = tuple(S["flag_col"])
        for g in self.groups:
            if not g["n"]:
                continue
            pi["growDur"].value = g["grow"]
            pi["bob"].value = g["bob"]
            pi["windows"].value = g["windows"]
            pi["shipMode"].value = g["ship"]
            pi["flagFromInst"].value = g["fromInst"]
            pi["worldMesh"].value = g["world"]
            g["vao"].render(instances=g["n"])
        pw = self.p_wat
        pw["VP"].write(gl(VP))
        self.set_common(pw, S)
        self.h_tex.use(2)
        pw["hTex"].value = 2
        self.w_tex.use(4)
        pw["wTex"].value = 4
        pw["hRect"].value = self.h_rect
        pw["skyTop"].value = tuple(S["sky_top"])
        pw["skyHor"].value = tuple(S["sky_hor"])
        self.vao_wat.render()
        if len(particles):
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            ctx.depth_mask = False
            pp = self.p_part
            pp["VP"].write(gl(VP))
            inv = np.linalg.inv(V)
            pp["camR"].value = tuple(inv[:3, 0])
            pp["camU"].value = tuple(inv[:3, 1])
            pp["camPos"].value = tuple(cam)
            pp["fogCol"].value = tuple(S["fog_col"])
            pp["fogDen"].value = S["fog_den"]
            part = np.asarray(particles, np.float32)[:6000]
            self.part_buf.write(part.tobytes())
            self.vao_part.render(instances=len(part))
            ctx.depth_mask = True
            ctx.disable(moderngl.BLEND)
        ctx.copy_framebuffer(self.resolve, self.msaa)
        # post
        self.out_fbo.use()
        ctx.disable(moderngl.DEPTH_TEST)
        self.scene_tex.use(0)
        self.overlay_tex.write(overlay_bytes)
        self.overlay_tex.use(3)
        pp = self.p_post
        pp["scene"].value = 0
        pp["overlay"].value = 3
        pp["tilt"].value = S.get("tilt", 1.0)
        pp["texel"].value = (1 / W, 1 / H)
        pp["fade"].value = S.get("fade", 1.0)
        pp["grade"].value = tuple(S.get("grade", (1.0, 1.0, 1.0)))
        self.vao_post.render()
        return self.out_fbo.read(components=3), VP
