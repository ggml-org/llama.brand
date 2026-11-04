<!-- From the + of C++ to the Llama icon, step by step: one timeline, every shape computed from the font and the icon. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { SIZE, SPLIT, corners, type Pt } from '#lib/logo.ts';

	const LEAN = 1 / Math.tan(Math.PI / 3); // 30° from upright: the shear that turns upright edges into 60° ones

	// eases: arms retract and lines draw with a quick start and a long settle; shape changes accelerate and settle
	const outQuart = (x: number) => 1 - (1 - x) ** 4;
	const outCubic = (x: number) => 1 - (1 - x) ** 3;
	const inOutCubic = (x: number) => (x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2);
	const inOutQuart = (x: number) => (x < 0.5 ? 8 * x ** 4 : 1 - (-2 * x + 2) ** 4 / 2);

	// the timeline, in seconds: each step overlaps the one before it, so the shape never stops moving
	const steps = [
		{ name: 'C++', from: 0, to: 0, ease: outCubic },
		{ name: 'Plus', from: 0.5, to: 1.3, ease: inOutQuart },
		{ name: 'L', from: 1.35, to: 1.95, ease: outQuart },
		{ name: 'Open the corner', from: 1.75, to: 2.3, ease: inOutCubic },
		{ name: 'Bolt', from: 2.1, to: 2.85, ease: outCubic },
		{ name: 'Lean', from: 2.65, to: 3.65, ease: inOutQuart },
		{ name: 'Soften', from: 3.45, to: 4.05, ease: outCubic }
	];
	const END = 4.4;

	let t = $state(0);
	let playing = $state(false);
	let root = $state<HTMLElement>();

	const clamp = (x: number) => Math.min(1, Math.max(0, x));
	const progress = (i: number) => {
		const { from, to, ease } = steps[i];
		return to <= from ? 1 : ease(clamp((t - from) / (to - from)));
	};
	const [, pPlus, pL, pOpen, pBolt, pLean, pSoft] = $derived(steps.map((_, i) => progress(i)));
	const current = $derived(Math.max(0, steps.findLastIndex((s) => t >= s.from)));

	// upright blocks, in upright coordinates (u across, y down), the same as the step tiles
	type Box = [number, number, number, number];
	const block: Record<string, Box> = { top: [-120, 0, 120, SPLIT], centre: [-120, SPLIT, 120, SIZE], right: [120, SPLIT, 480, SIZE], left: [-480, SPLIT, -120, SIZE], bottom: [-120, SIZE, 120, SIZE + SPLIT] };

	// the lean pivots on the baseline (y = SIZE), so the feet stay put while the tops slide right
	const shearPt = ([u, y]: Pt, k: number): Pt => [u + (SIZE - y) * k, y];
	const poly = ([u0, y0, u1, y1]: Box, k = 0) => {
		const pts = ([[u0, y0], [u1, y0], [u1, y1], [u0, y1]] as Pt[]).map((p) => shearPt(p, k));
		return `M${pts.map((p) => p.join(' ')).join('L')}Z`;
	};
	const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
	const lerpBox = (a: Box, b: Box, p: number) => a.map((v, i) => lerp(v, b[i], p)) as Box;

	// "C++" set in Llama Sans Display Bold (font units, y up), placed so the middle + is centred on the plus.
	// Its + is two 114-unit bars, so it splits into the same five blocks, and each block grows into its own.
	const GLYPH = {
		C: 'M361 -16Q264 -16 189 28Q146 54 116 90Q85 126 66 169Q47 212 38 259Q30 306 30 354Q30 467 71 551Q112 635 187 680Q262 726 363 726Q500 726 576 658Q648 594 672 479L528 457Q516 527 474 567Q433 606 363 606Q304 606 262 575Q228 549 209 513Q190 477 182 436Q175 394 175 354Q175 276 198 221Q219 169 262 137Q304 105 362 105Q437 105 479 147Q520 189 531 264L676 244Q662 167 624 110Q594 66 552 38Q511 10 462 -3Q412 -16 361 -16Z',
		plus: 'M214 44V231H27V345H214V532H328V345H515V231H328V44Z',
		advance: { C: 703, plus: 542 }
	};
	const S = 1.25; // font units to drawing units
	const MID = GLYPH.advance.C; // the middle + starts where the C ends
	const X = -(MID + 271) * S, Y = (SPLIT + SIZE) / 2 + 288 * S; // the middle + centred on the plus centre
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
	const top = $derived(pSoft > 0 ? blade(0, pSoft) : poly(at.top, k));
	const foot = $derived(pSoft > 0 ? blade(1, pSoft) : poly(at.right, k));

	// a classic lightning bolt on the icon's own 60° edges (as in step 04), drawn in, then let go once the blades fit it
	const bolt = 'M226.15 0H466.15L346 208H520L224.4 720L300 392H0Z';

	// the camera: the word, then the whole plus, then the icon. Each frame is a box to fit (centre, width, height),
	// fitted to the stage's own shape so the wide word fills a wide stage
	type Frame = [number, number, number, number];
	const word: Frame = [X + 895 * S, Y - 355 * S, 1730 * S * 1.18, 742 * S * 1.5]; // the word's ink, with a margin
	const plusFrame: Frame = [0, (SIZE + SPLIT) / 2, 1120, 1120]; // the plus runs 0 to SIZE + SPLIT
	const iconFrame: Frame = [300, 300, 1000, 1000];
	let stageW = $state(16);
	let stageH = $state(10);
	const fit = ([cx, cy, w, h]: Frame) => {
		const aspect = stageW / stageH;
		const vw = w / h > aspect ? w : h * aspect;
		return [cx, cy, vw] as const;
	};
	const view = $derived.by(() => {
		const a = fit(word), b = fit(plusFrame), c = fit(iconFrame);
		const p1 = inOutCubic(clamp((t - steps[1].from) / (steps[1].to - steps[1].from)));
		const p2 = inOutCubic(clamp((t - steps[2].from) / (steps[5].to - steps[2].from)));
		const [cx, cy, vw] = a.map((v, i) => lerp(lerp(v, b[i], p1), c[i], p2));
		const vh = vw / (stageW / stageH);
		return `${cx - vw / 2} ${cy - vh / 2} ${vw} ${vh}`;
	});

	let frame = 0;
	let last = 0;
	function tick(now: number) {
		t = Math.min(END, t + (now - last) / 1000);
		last = now;
		if (t < END && playing) frame = requestAnimationFrame(tick);
		else playing = false;
	}
	function play() {
		if (t >= END) t = 0;
		playing = true;
		last = performance.now();
		frame = requestAnimationFrame(tick);
	}
	function pause() {
		playing = false;
		cancelAnimationFrame(frame);
	}
	const seek = (to: number) => {
		pause();
		t = to;
	};

	// play once when the stage first comes into view; with reduced motion it waits for the play button
	onMount(() => {
		if (matchMedia('(prefers-reduced-motion: reduce)').matches || !root) return pause;
		const seen = new IntersectionObserver(([e]) => {
			if (!e.isIntersecting) return;
			seen.disconnect();
			setTimeout(play, 200);
		}, { threshold: 0.6 });
		seen.observe(root);
		return () => {
			seen.disconnect();
			pause();
		};
	});
</script>

<figure class="morph" bind:this={root}>
	<div class="stage" bind:clientWidth={stageW} bind:clientHeight={stageH}>
	<svg viewBox={view} role="img" aria-label="Animation: the + of C++ becomes a plus, then an L, opens its corner, takes a bolt’s slant and softens into the Llama icon. Now showing: {steps[current].name}">
		<!-- the rest of "C++": the C and the second + step aside and fade -->
		<g style:opacity={1 - aside}>
			<path d={GLYPH.C} class="fill" transform="translate({X - 160 * aside} {Y}) scale({S} {-S})" />
			<path d={GLYPH.plus} class="fill" transform="translate({X + (MID + GLYPH.advance.plus) * S + 160 * aside} {Y}) scale({S} {-S})" />
		</g>
		<g transform="matrix(1 0 {-k} 1 {SIZE * k} 0)">
			<!-- the arms that go: they retract, and a faint outline of where they were stays until the lean -->
			{#each going as g, i (i)}
				<path d={poly(g.was)} class="ghost" style:opacity={0.7 * g.p * (1 - pLean)} />
				<path d={poly(g.now)} class="fill" style:opacity={1 - g.p ** 3} />
			{/each}
		</g>
		<!-- while the centre block still touches them, a hairline in their own colour closes the anti-aliasing seams -->
		<path d={top} class="blade" style:stroke-opacity={1 - pOpen} />
		<path d={foot} class="blade" style:stroke-opacity={1 - pOpen} />
		<path d={bolt} pathLength="1" class="bolt" style:stroke-dashoffset={1 - pBolt} style:opacity={1 - pSoft} />
	</svg>
	</div>

	<figcaption class="controls">
		<button type="button" class="play" onclick={() => (playing ? pause() : play())} aria-label={playing ? 'Pause' : t >= END ? 'Replay' : 'Play'}>
			{#if playing}
				<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" /></svg>
			{:else if t >= END}
				<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3a5 5 0 1 0 5 5h-1.6A3.4 3.4 0 1 1 8 4.6V7l3.5-3.2L8 .6z" /></svg>
			{:else}
				<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5z" /></svg>
			{/if}
		</button>
		<input type="range" min="0" max={END} step="0.01" value={t} oninput={(e) => seek(+e.currentTarget.value)} aria-label="Position in the animation" />
		<ol class="labels">
			{#each steps as s, i (s.name)}
				<li>
					<button type="button" class:on={i === current} onclick={() => seek(Math.max(s.to, s.from))}>
						<span>{String(i).padStart(2, '0')}</span>{s.name}
					</button>
				</li>
			{/each}
		</ol>
	</figcaption>
</figure>

<style>
	.morph {
		margin: 0;
		display: grid;
		border-radius: 12px;
		background: var(--l-panel);
		overflow: hidden;
	}
	/* a wide stage for the word, a square one on phones; the camera fits each frame to whatever shape it gets */
	.stage {
		aspect-ratio: 16 / 10;
		max-height: 62vh;
	}
	@media (max-width: 600px) {
		.stage {
			aspect-ratio: 1;
		}
	}
	.stage svg {
		display: block;
		width: 100%;
		height: 100%;
	}
	.blade,
	.fill {
		fill: var(--l-shape);
		stroke: var(--l-shape);
		stroke-width: 1;
		vector-effect: non-scaling-stroke;
	}
	.ghost {
		fill: none;
		stroke: var(--l-line);
		stroke-width: 1.5;
		vector-effect: non-scaling-stroke;
	}
	.bolt {
		/* drawn in with a dash over pathLength 1, so the stroke scales with the drawing (no non-scaling-stroke) */
		fill: none;
		stroke: var(--l-ink);
		stroke-width: 4;
		stroke-linejoin: round;
		stroke-dasharray: 1;
	}
	.controls {
		display: grid;
		grid-template-columns: auto 1fr;
		align-items: center;
		gap: 10px 12px;
		padding: 12px 16px 16px;
		border-top: 1px solid var(--l-rule);
	}
	.play {
		display: grid;
		place-items: center;
		width: 36px;
		height: 36px;
		padding: 0;
		border: 0;
		border-radius: 50%;
		background: var(--l-ink);
		color: var(--l-bg);
		cursor: pointer;
	}
	.play svg {
		width: 14px;
		height: 14px;
		fill: currentColor;
	}
	input[type='range'] {
		width: 100%;
		accent-color: var(--l-ink);
	}
	.labels {
		grid-column: 1 / -1;
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.labels button {
		display: flex;
		gap: 6px;
		padding: 0.35em 0.8em;
		border: 0;
		border-radius: 999px;
		background: none;
		box-shadow: inset 0 0 0 1px var(--l-rule);
		color: var(--l-muted);
		font: 500 13px / normal 'Llama Sans UI', var(--body);
		cursor: pointer;
		transition: background-color 200ms ease, color 200ms ease;
	}
	.labels button span {
		font: 500 11px / 1.6 var(--mono);
		opacity: 0.7;
	}
	.labels button.on {
		background: var(--l-ink);
		color: var(--l-bg);
	}
	.play:focus-visible,
	.labels button:focus-visible {
		outline: 2px solid var(--l-ink);
		outline-offset: 2px;
	}
</style>
