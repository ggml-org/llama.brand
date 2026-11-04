<!-- From the + of C++ to the Llama icon: the shapes of the origin animation, drawn into the blueprint's own drawing.
     The hero owns the clock (t) and the camera; this layer only draws what t asks for, and fades out as the
     blueprint's outlined parts take over. -->
<svelte:options namespace="svg" />

<script lang="ts">
	import { SIZE, SPLIT, corners, type Pt } from '#lib/logo.ts';
	import { steps, progress, span, lerp, clamp, outCubic, GLYPH, S, MID, X, Y, WORD, WX, BECOMES, BOUNDS, STEP, LIGHTNING, BLUEPRINT, BLUEPRINT_STEP } from '#lib/origin.ts';

	let { t }: { t: number } = $props();

	const LEAN = 1 / Math.tan(Math.PI / 3); // 30° from upright: the shear that turns upright edges into 60° ones

	const [, pCpp, pPlus, pL, pOpen, pLean, pBolt, pSoft, pFill] = $derived(steps.slice(0, 9).map((_, i) => progress(t, i)));
	// a line drawing, like the sketches, until the icon is finished; then it fills in, just before the blueprint
	// the blueprint's outlined parts take over from the solid icon
	const B0 = steps[BLUEPRINT_STEP].from;
	const gone = $derived(span(t, B0 + BLUEPRINT.parts[0], B0 + BLUEPRINT.parts[1]));

	// upright blocks, in upright coordinates (u across, y down), the same as the step tiles
	type Box = [number, number, number, number];
	const block: Record<string, Box> = { top: [-120, 0, 120, SPLIT], centre: [-120, SPLIT, 120, SIZE], right: [120, SPLIT, 480, SIZE], left: [-480, SPLIT, -120, SIZE], bottom: [-120, SIZE, 120, SIZE + SPLIT] };

	// the lean pivots on the baseline (y = SIZE), so the feet stay put while the tops slide right
	const shearPt = ([u, y]: Pt, k: number): Pt => [u + (SIZE - y) * k, y];
	const poly = ([u0, y0, u1, y1]: Box, k = 0) => {
		const pts = ([[u0, y0], [u1, y0], [u1, y1], [u0, y1]] as Pt[]).map((p) => shearPt(p, k));
		return `M${pts.map((p) => p.join(' ')).join('L')}Z`;
	};
	const lerpBox = (a: Box, b: Box, p: number) => a.map((v, i) => lerp(v, b[i], p)) as Box;

	// the middle + of "C++" as five blocks, each growing into the plus's own
	const glyphBox = (x0: number, x1: number, ylo: number, yhi: number): Box => [X + (MID + x0) * S, Y - yhi * S, X + (MID + x1) * S, Y - ylo * S];
	const fromGlyph: Record<string, Box> = {
		top: glyphBox(214, 328, 345, 532),
		centre: glyphBox(214, 328, 231, 345),
		right: glyphBox(328, 515, 231, 345),
		left: glyphBox(27, 214, 231, 345),
		bottom: glyphBox(214, 328, 44, 231)
	};
	const at = $derived(Object.fromEntries(Object.keys(block).map((b) => [b, lerpBox(fromGlyph[b], block[b], pPlus)])) as Record<string, Box>);
	// the C and the other + step aside and fade while the middle + grows
	const plusStep = steps[STEP.Plus];
	const aside = $derived(outCubic(clamp((t - plusStep.from) / ((plusStep.to - plusStep.from) * 0.7))));
	// the plus's blocks take over from the middle + of "C++" just as it starts to grow
	const blocks = $derived(clamp((t - plusStep.from) / 0.2));

	// "llama.cpp": "llama." steps aside and fades while c becomes C and each p a +. Each pair shares one box that
	// moves from the letter's to its counterpart's, and the two cross-fade inside it, so the letter reshapes in place
	const cppStep = steps[STEP['C++']];
	const leave = $derived(outCubic(clamp((t - cppStep.from) / ((cppStep.to - cppStep.from) * 0.6))));
	const boxAt = (b: number[], ox: number): Box => [ox + b[0] * S, Y - b[3] * S, ox + b[2] * S, Y - b[1] * S];
	function into(b: number[], ox: number, box: Box) {
		const src = boxAt(b, ox);
		const kx = (box[2] - box[0]) / (src[2] - src[0]), ky = (box[3] - box[1]) / (src[3] - src[1]);
		return `translate(${box[0] - src[0] * kx} ${box[1] - src[1] * ky}) scale(${kx} ${ky}) translate(${ox} ${Y}) scale(${S} ${-S})`;
	}
	const letters = $derived(
		WORD.layout.map(([ch, x], i) => {
			const g = WORD.glyphs[ch], ox = WX + x * S, to = BECOMES[i];
			if (!to) return { i, d: g.d, transform: `translate(${ox - 200 * leave} ${Y}) scale(${S} ${-S})`, opacity: 1 - leave };
			const tox = X + to.x * S, tb = BOUNDS[to.to];
			const box = lerpBox(boxAt(g.bounds, ox), boxAt(tb, tox), pCpp);
			// C and the second + hand over to the "C++" drawn below once they land; the middle + to the plus's blocks
			const stays = i === 7 ? 1 - blocks : pCpp < 1 ? 1 : 0;
			return { i, d: g.d, transform: into(g.bounds, ox, box), opacity: 1 - pCpp, to: { d: GLYPH[to.to], transform: into(tb, tox, box), opacity: pCpp * stays } };
		})
	);

	// the arms that go slide back into the centre; the centre then folds into the point where stem and foot meet
	const going = $derived.by(() => {
		const [l, b, c] = [at.left, at.bottom, at.centre];
		return [
			{ was: block.left, now: [lerp(l[0], l[2], pL), l[1], l[2], l[3]] as Box, p: pL },
			{ was: block.bottom, now: [b[0], b[1], b[2], lerp(b[3], b[1], pL)] as Box, p: pL },
			{ was: block.centre, now: [lerp(c[0], c[2], pOpen), c[1], c[2], lerp(c[3], c[1], pOpen)] as Box, p: pOpen }
		];
	});

	// the finished blades with their outer corners rounded by s (0 sharp, 1 the brand's own curve)
	const towards = (a: Pt, b: Pt, s: number): Pt => [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s];
	function blade(i: 0 | 1, s: number) {
		const c = corners[i];
		const e = towards(c.sharp, c.tangentEdge, s).join(' ');
		const f = towards(c.sharp, c.tangentFlat, s).join(' ');
		const r = c.r * s;
		return i === 0
			? `M0 ${SPLIT}L${e}A${r} ${r} 0 0 1 ${f}L466.154 0L240 ${SPLIT}Z`
			: `M240 ${SPLIT}L600 ${SPLIT}L${e}A${r} ${r} 0 0 1 ${f}L120 ${SIZE}Z`;
	}
	const k = $derived(LEAN * pLean);

	// the strike: a lightning bolt fitted to the L races down over it from the top, flares, flickers once and dies
	// away in yellow, with a glow; the L itself keeps its shape and only catches a little of the light
	const round = $derived(outCubic(clamp(pSoft)));
	const strike = $derived(pBolt <= 0 || pBolt >= 1 ? 0 : pBolt < 0.06 ? pBolt / 0.06 : pBolt < 0.13 ? lerp(1, 0.3, (pBolt - 0.06) / 0.07) : pBolt < 0.2 ? lerp(0.3, 1, (pBolt - 0.13) / 0.07) : 1 - outCubic((pBolt - 0.2) / 0.8));
	const reach = $derived(-20 + 1100 * outCubic(clamp(pBolt / 0.08))); // how far down the strike has got: past the tip (y 784) and its glow
	const flash = $derived(`${Math.round(strike * 100)}%`); // scaled by the theme's --l-bolt-tint
	const top = $derived(round > 0 ? blade(0, round) : poly(at.top, k));
	const foot = $derived(round > 0 ? blade(1, round) : poly(at.right, k));
</script>

{#if gone < 1}
	<g class="morph" style:opacity={1 - gone} style:--solid={pFill}>
		<defs>
			<filter id="strike-glow" filterUnits="userSpaceOnUse" x="-400" y="-400" width="1400" height="1600">
				<feGaussianBlur stdDeviation="28" />
			</filter>
			<clipPath id="strike-reach"><rect x="-400" y="-40" width="1400" height={Math.max(0, reach + 40)} /></clipPath>
		</defs>

		<!-- "llama.cpp", becoming "C++" -->
		{#if blocks < 1}
			{#each letters as l (l.i)}
				{#if l.opacity > 0}<path d={l.d} class="fill" transform={l.transform} style:opacity={l.opacity} />{/if}
				{#if l.to && l.to.opacity > 0}<path d={l.to.d} class="fill" transform={l.to.transform} style:opacity={l.to.opacity} />{/if}
			{/each}
		{/if}
		<!-- the rest of "C++": the C and the second + step aside and fade -->
		{#if pCpp >= 1 && aside < 1}
			<g style:opacity={1 - aside}>
				<path d={GLYPH.C} class="fill" transform="translate({X - 160 * aside} {Y}) scale({S} {-S})" />
				<path d={GLYPH.plus} class="fill" transform="translate({X + (MID + GLYPH.advance.plus) * S + 160 * aside} {Y}) scale({S} {-S})" />
			</g>
		{/if}
		<g style:opacity={blocks}>
		<g transform="matrix(1 0 {-k} 1 {SIZE * k} 0)">
			<!-- the arms that go: they retract, and a faint outline of where they were stays until the lean -->
			{#each going as g, i (i)}
				<path d={poly(g.was)} class="ghost" style:opacity={0.7 * g.p * (1 - pLean)} />
				<path d={poly(g.now)} class="fill" style:opacity={1 - g.p ** 6} />
			{/each}
		</g>
		<path d={top} class="blade" style:--flash={flash} />
		<path d={foot} class="blade" style:--flash={flash} />
		</g>
		<!-- the strike, over the L: a blurred yellow flare and the bolt itself, revealed from the top down -->
		{#if strike > 0}
			<g clip-path="url(#strike-reach)" style:opacity={strike}>
				<path d={LIGHTNING} class="flare" filter="url(#strike-glow)" />
				<path d={LIGHTNING} class="bolt" />
			</g>
		{/if}
	</g>
{/if}

<style>
	.morph {
		pointer-events: none;
	}
	/* outlines in the icon's own colour, filled only once the icon is finished (--solid) */
	.fill,
	.blade {
		fill: var(--l-shape);
		fill-opacity: var(--solid, 0);
		stroke: var(--l-shape);
		stroke-width: 2;
		stroke-linejoin: round;
		vector-effect: non-scaling-stroke;
	}
	/* the one colour on the page: the lightning; the outlined L catches a little of its light */
	.blade {
		stroke: color-mix(in srgb, var(--l-bolt) calc(var(--flash, 0%) * var(--l-bolt-tint)), var(--l-shape));
	}
	.ghost {
		fill: none;
		stroke: var(--l-line);
		stroke-width: 1.5;
		vector-effect: non-scaling-stroke;
	}
	.flare {
		fill: var(--l-bolt);
		opacity: 0.8;
	}
	.bolt {
		fill: var(--l-bolt);
		fill-opacity: var(--l-bolt-alpha);
	}
</style>
