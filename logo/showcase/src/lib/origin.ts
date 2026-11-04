// The origin animation's timeline: from the + of C++ to the Llama icon, then into the blueprint.
// Everything is in the icon's own coordinates (the 600 x 600 drawing), so it shares the blueprint's frame.
import { SIZE, SPLIT } from './logo.ts';

export const clamp = (x: number) => Math.min(1, Math.max(0, x));
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

// arms retract and lines draw with a quick start and a long settle; shape changes accelerate and settle
export const outQuart = (x: number) => 1 - (1 - x) ** 4;
export const outCubic = (x: number) => 1 - (1 - x) ** 3;
export const inOutCubic = (x: number) => (x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2);
export const inOutQuart = (x: number) => (x < 0.5 ? 8 * x ** 4 : 1 - (-2 * x + 2) ** 4 / 2);
const linear = (x: number) => x;

// each step overlaps the one before it, so the shape never stops moving (seconds)
export const steps = [
	{ name: 'C++', from: 0, to: 0, ease: outCubic, note: 'It begins with the + of C++, the language llama.cpp is written in.' },
	{ name: 'Plus', from: 0.5, to: 1.3, ease: inOutQuart, note: 'Its plus grows the icon’s own arms: 240 wide upright, 208 deep across.' },
	{ name: 'L', from: 1.35, to: 1.95, ease: outQuart, note: 'Keep the top arm, the centre and the right arm: an L inside the +.' },
	{ name: 'Open the corner', from: 1.75, to: 2.3, ease: inOutCubic, note: 'Lift out the centre block. Stem and foot now touch at one point.' },
	{ name: 'Lean', from: 2.15, to: 3.05, ease: inOutQuart, note: 'Slant it 30° on the baseline: every edge now runs at 60°.' },
	{ name: 'Bolt', from: 3.05, to: 3.85, ease: linear, note: 'Lightning strikes through the slanted L, cut along the blade’s diagonal and turned about the joint: speed, which is what llama.cpp is about.' },
	{ name: 'Soften', from: 3.75, to: 4.55, ease: linear, note: 'Round only the two outer corners.' },
	{ name: 'Fill', from: 4.5, to: 4.95, ease: inOutCubic, note: 'Fill it in: the Llama icon.' },
	{ name: 'Blueprint', from: 5.0, to: 6.25, ease: linear, note: 'And this is how it is built.' }
];
export const END = 6.4;
export const BLUEPRINT_STEP = steps.length - 1;
/** When each part of the blueprint fades in, in seconds after the Blueprint step starts. */
export const BLUEPRINT = { grid: [0.1, 0.6], parts: [0.25, 0.75], lines: [0.3, 0.85], dims: [0.55, 1.05], title: [0.8, 1.25] } as const;

/** How far step i has got at time t, eased (0 before it starts, 1 once it is done). */
export function progress(t: number, i: number) {
	const { from, to, ease } = steps[i];
	return to <= from ? 1 : ease(clamp((t - from) / (to - from)));
}
/** An eased 0 to 1 over a window of seconds, for the parts of the blueprint that fade in one after another. */
export const span = (t: number, from: number, to: number) => inOutCubic(clamp((t - from) / (to - from)));
export const stepAt = (t: number) => Math.max(0, steps.findLastIndex((s) => t >= s.from));

// "C++" set in Llama Sans Display Bold (font units, y up), placed so its middle + is centred on the plus.
// Its + is two 114-unit bars, so it splits into the same five blocks as the plus, and each block grows into its own.
export const GLYPH = {
	C: 'M361 -16Q264 -16 189 28Q146 54 116 90Q85 126 66 169Q47 212 38 259Q30 306 30 354Q30 467 71 551Q112 635 187 680Q262 726 363 726Q500 726 576 658Q648 594 672 479L528 457Q516 527 474 567Q433 606 363 606Q304 606 262 575Q228 549 209 513Q190 477 182 436Q175 394 175 354Q175 276 198 221Q219 169 262 137Q304 105 362 105Q437 105 479 147Q520 189 531 264L676 244Q662 167 624 110Q594 66 552 38Q511 10 462 -3Q412 -16 361 -16Z',
	plus: 'M214 44V231H27V345H214V532H328V345H515V231H328V44Z',
	advance: { C: 703, plus: 542 }
};
export const S = 1.25; // font units to drawing units
export const MID = GLYPH.advance.C; // the middle + starts where the C ends
export const X = -(MID + 271) * S; // the middle + centred on the plus centre
export const Y = (SIZE + SPLIT) / 2 + 288 * S;

// the camera: the word, then the whole plus, then the icon, then out to the blueprint's own frame.
// Each frame is a box to fit (centre x, centre y, width, height), fitted to the stage's shape.
export type Frame = [number, number, number, number];
const word: Frame = [X + 895 * S, Y - 355 * S, 1730 * S * 1.35, 742 * S * 1.7];
const plusFrame: Frame = [0, (SIZE + SPLIT) / 2, 1300, 1300]; // the plus runs 0 to SIZE + SPLIT
const iconFrame: Frame = [300, 400, 1300, 1300]; // room below for the lightning's tip and its glow

export function camera(t: number, aspect: number, final: Frame) {
	const fit = ([cx, cy, w, h]: Frame) => [cx, cy, w / h > aspect ? w : h * aspect];
	const frames = [word, plusFrame, iconFrame, final].map(fit);
	const legs = [
		inOutCubic(clamp((t - steps[1].from) / (steps[1].to - steps[1].from))),
		inOutCubic(clamp((t - steps[2].from) / (steps[4].to - steps[2].from))),
		inOutCubic(clamp((t - steps[BLUEPRINT_STEP].from) / 0.8))
	];
	let [cx, cy, vw] = frames[0];
	legs.forEach((p, i) => ([cx, cy, vw] = [cx, cy, vw].map((v, j) => lerp(v, frames[i + 1][j], p))));
	const vh = vw / aspect;
	return `${cx - vw / 2} ${cy - vh / 2} ${vw} ${vh}`;
}

// the lightning that strikes over the leaned L, after the sketch: the upper blade cut along its diagonal, from its
// bottom-left corner to its top-right one, keeps its lower-right half; the lower half is that same triangle turned
// 180° about the joint. So its top runs along the foot's top edge, its left side is the foot's left 60° edge carried
// on down, its long side runs parallel to the upper diagonal, and it ends in a tip below and left of the foot.
const turn = ([x, y]: [number, number]): [number, number] => [2 * 240 - x, 2 * SPLIT - y]; // 180° about the joint
const upper: [number, number][] = [[466.154, 0], [0, SPLIT], [240, SPLIT]];
const lower = upper.map(turn);
export const TIP = lower[0]; // (14, 784)
const tri = (pts: [number, number][]) => `M${pts.map((p) => p.join(' ')).join('L')}Z`;
export const LIGHTNING = tri(upper) + tri(lower);
