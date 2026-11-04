<!-- From the + of C++ to the Llama icon: the shapes of the origin animation, drawn into the blueprint's own drawing.
     The hero owns the clock (t) and the camera; this layer only draws what t asks for, and fades out as the
     blueprint's outlined parts take over. -->
<svelte:options namespace="svg" />

<script lang="ts">
	import { SIZE, SPLIT, corners, type Pt } from '#lib/logo.ts';
	import { steps, progress, span, lerp, clamp, outCubic, GLYPH, S, MID, X, Y, LIGHTNING, BLUEPRINT, BLUEPRINT_STEP } from '#lib/origin.ts';

	let { t }: { t: number } = $props();

	const LEAN = 1 / Math.tan(Math.PI / 3); // 30° from upright: the shear that turns upright edges into 60° ones

	const [, pPlus, pL, pOpen, pLean, pBolt, pSoft, pFill] = $derived(steps.slice(0, 8).map((_, i) => progress(t, i)));
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
	const aside = $derived(outCubic(clamp((t - steps[1].from) / ((steps[1].to - steps[1].from) * 0.7))));

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

		<!-- the rest of "C++": the C and the second + step aside and fade -->
		{#if aside < 1}
			<g style:opacity={1 - aside}>
				<path d={GLYPH.C} class="fill" transform="translate({X - 160 * aside} {Y}) scale({S} {-S})" />
				<path d={GLYPH.plus} class="fill" transform="translate({X + (MID + GLYPH.advance.plus) * S + 160 * aside} {Y}) scale({S} {-S})" />
			</g>
		{/if}
		<g transform="matrix(1 0 {-k} 1 {SIZE * k} 0)">
			<!-- the arms that go: they retract, and a faint outline of where they were stays until the lean -->
			{#each going as g, i (i)}
				<path d={poly(g.was)} class="ghost" style:opacity={0.7 * g.p * (1 - pLean)} />
				<path d={poly(g.now)} class="fill" style:opacity={1 - g.p ** 6} />
			{/each}
		</g>
		<path d={top} class="blade" style:--flash={flash} />
		<path d={foot} class="blade" style:--flash={flash} />
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
