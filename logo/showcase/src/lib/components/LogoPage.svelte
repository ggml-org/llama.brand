<!-- The Llama icon taken apart: it grows out of the + of C++ into the mark and settles into its blueprint, then each rule that shapes it. -->
<script lang="ts">
	import { onMount, type Snippet } from 'svelte';
	import Morph from './Morph.svelte';
	import { PATHS, SIZE, SPLIT, edges, corners, angle, extend, type Pt } from '#lib/logo.ts';
	import { steps as originSteps, END, BLUEPRINT, BLUEPRINT_STEP, STEP, LIGHTNING, camera, span, stepAt } from '#lib/origin.ts';

	const box: [number, number, number, number] = [-320, -160, 920, 760];
	const vb = `${box[0]} ${box[1]} ${box[2] - box[0]} ${box[3] - box[1]}`;

	// perpendicular to the 60° edges, through a point
	const sh = edges.shared;
	const dir: Pt = [sh[1][0] - sh[0][0], sh[1][1] - sh[0][1]];
	const perp = (p: Pt): [Pt, Pt] => [p, [p[0] - dir[1], p[1] + dir[0]]];

	// every part of the blueprint belongs to one idea of the mark; hovering or tapping a part highlights its idea
	// (null: plain construction, such as the overall frame, which only fades back with the rest)
	type Feature = 'upper' | 'lower' | 'angle' | 'split' | 'steps' | 'corners';
	type Tag = Feature | null;
	type Line = { a: Pt; b: Pt; f: Tag };
	const vertical = (x: number, f: Tag): [Pt, Pt, Tag] => [[x, 0], [x, 1], f];
	const horizontal = (y: number, f: Tag): [Pt, Pt, Tag] => [[0, y], [1, y], f];
	const STEPS = [0, 120, 240, 360, 480, 600]; // five steps of 120 across the drawing
	const lines: Line[] = (
		[
			...STEPS.map((x) => vertical(x, 'steps')),
			vertical(corners[0].tangentFlat[0], 'corners'),
			vertical(corners[1].tangentFlat[0], 'corners'),
			vertical(466.154, 'upper'),
			horizontal(0, null),
			horizontal(SPLIT, 'split'),
			horizontal(SIZE, null),
			horizontal(corners[0].centre[1], 'corners'),
			horizontal(corners[1].centre[1], 'corners'),
			[...edges.upperLeft, 'angle'],
			[...edges.shared, 'angle'],
			[...edges.lowerRight, 'angle'],
			...[[240, SPLIT], [0, SPLIT], [SIZE, SPLIT], [120, SIZE], [466.154, 0]].map(
				(p) => [...perp(p as Pt), 'angle'] as [Pt, Pt, Tag]
			)
		] as [Pt, Pt, Tag][]
	).map(([a, b, f]) => {
		const [p, q] = extend(a, b, box);
		return { a: p, b: q, f };
	});


	// blueprint dimensions: two end points, a tick offset, where the label sits
	type Dim = { a: Pt; b: Pt; t: Pt; at: Pt; label: string; f: Tag; rot?: boolean };
	const h = (y: number, x0: number, x1: number, label: string, f: Tag): Dim =>
		({ a: [x0, y], b: [x1, y], t: [0, 10], at: [(x0 + x1) / 2, y - 12], label, f });
	const v = (x: number, y0: number, y1: number, label: string, f: Tag): Dim =>
		({ a: [x, y0], b: [x, y1], t: [10, 0], at: [x - 12, (y0 + y1) / 2], label, f, rot: true });
	const dims: Dim[] = [
		h(-100, 0, SIZE, `${SIZE}`, null),
		h(-50, 226.15, 466.154, '240', 'upper'),
		v(-100, 0, SPLIT, `${SPLIT}`, 'split'),
		v(-100, SPLIT, SIZE, `${SIZE - SPLIT}`, 'split'),
		v(-160, 0, SIZE, `${SIZE}`, null),
		...STEPS.slice(1).map((x) => h(690, x - 120, x, '120', 'steps')),
		h(740, 240, SIZE, `${SIZE - 240}`, 'lower')
	];

	const deg = angle(...edges.upperLeft).toFixed(1);
	const lower = SIZE - SPLIT;
	const r = Math.round(corners[0].r);
	const trim = Math.round(corners[0].trim);

	const features: { f: Feature; name: string; note: string }[] = [
		{ f: 'upper', name: 'Upper blade', note: `The tall blade, ${SPLIT} high and 240 across: the top arm of the plus.` },
		{ f: 'lower', name: 'Lower blade', note: `The foot, ${lower} high and 360 across: the plus’s right arm.` },
		{ f: 'angle', name: `${Math.round(+deg)}° edges`, note: `Every slanted edge runs at ${deg}°, and the cross lines stand square to them.` },
		{ f: 'split', name: 'Split', note: `${SPLIT} above, ${lower} below: close to two thirds to one third.` },
		{ f: 'steps', name: 'Steps of 120', note: `Five steps of 120 span the ${SIZE}: the feet start at 0 and 120, the blades meet on 240, the foot’s corner lands on 480.` },
		{ f: 'corners', name: 'Soft corners', note: `Only the two outer corners round off, cut back ${trim} on circles of radius ≈ ${r}.` }
	];
	let hovered = $state<Feature | null>(null);
	let pinned = $state<Feature | null>(null);
	let touring = $state<Feature | null>(null);
	const active = $derived(hovered ?? pinned ?? touring);

	// once the origin animation has settled into the blueprint, light each idea up in turn; any hover, tap or focus ends it
	let timers: ReturnType<typeof setTimeout>[] = [];
	function stopTour() {
		timers.forEach(clearTimeout);
		timers = [];
		touring = null;
	}
	function startTour() {
		stopTour();
		timers = [...features.map((x) => x.f), null].map((f, i) => setTimeout(() => (touring = f), 300 + i * 600));
	}

	// the origin animation's clock: it plays once on load, from the + of C++ into this very blueprint
	let t = $state(0);
	let playing = $state(false);
	const done = $derived(t >= END);
	let frame = 0;
	let last = 0;
	function tick(now: number) {
		t = Math.min(END, t + (now - last) / 1000);
		last = now;
		if (t < END && playing) frame = requestAnimationFrame(tick);
		else if (playing) {
			playing = false;
			startTour();
		}
	}
	function play() {
		stopTour();
		hovered = pinned = null;
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
		stopTour();
		t = to;
	};
	onMount(() => {
		// with reduced motion, the page opens on the finished blueprint and the animation waits for the play button
		if (matchMedia('(prefers-reduced-motion: reduce)').matches) t = END;
		else document.fonts.ready.then(() => setTimeout(play, 250));
		return () => {
			pause();
			stopTour();
		};
	});

	// the camera ends on the blueprint's own frame, so the last frame of the animation is the blueprint as drawn
	const final: [number, number, number, number] = [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2, box[2] - box[0], box[3] - box[1]];
	const view = $derived(done ? vb : camera(t, final[2] / final[3], final));
	// the blueprint's layers fade in one after another as the animation hands over
	const B0 = originSteps[BLUEPRINT_STEP].from;
	const fade = $derived(
		Object.fromEntries(Object.entries(BLUEPRINT).map(([k, [a, b]]) => [k, done ? 1 : span(t, B0 + a, B0 + b)])) as Record<keyof typeof BLUEPRINT, number>
	);
	const step = $derived(stepAt(t));
	// the steps that have a tile below carry its number (01 Plus to 06 Soften)
	const stepNumber = (i: number) => (i >= STEP.Plus && i <= STEP.Soften ? `${String(i - STEP.Plus + 1).padStart(2, '0')} ` : '');
	const current = $derived(features.find((x) => x.f === active));
	const featureAt = (e: Event) => ((e.target as Element).closest('[data-f]') as HTMLElement | null)?.dataset.f as Feature | undefined;
	const pin = (f: Feature) => (pinned = pinned === f ? null : f);


	// where it comes from: undo the lean and the icon is an upright + and L on a 120 grid. The plus already has the
	// icon's own arms, mirrored: upright arms 240 wide and 392 long, side arms 208 deep and 360 long. The upper blade
	// is its top arm, the foot its right arm, and the centre block they would share is left out.
	const lean = 1 / Math.tan(Math.PI / 3); // 30° from upright
	const sheared = `matrix(1 0 ${-lean} 1 ${SIZE * lean} 0)`; // pivots on the baseline, so the feet stay put
	const rect = ([u0, y0, u1, y1]: number[]) => `M${u0} ${y0}H${u1}V${y1}H${u0}Z`;
	const arm = {
		top: [-120, 0, 120, SPLIT],
		centre: [-120, SPLIT, 120, SIZE],
		right: [120, SPLIT, 480, SIZE],
		left: [-480, SPLIT, -120, SIZE],
		bottom: [-120, SIZE, 120, SIZE + SPLIT]
	};
	const plus = Object.values(arm).map(rect);
	const parts = [rect(arm.top), rect(arm.right)];
	// a classic lightning bolt drawn on the icon's own 60° edges
	const bolt = 'M226.15 0H466.15L346 208H520L224.4 720L300 392H0Z';
	// one scale for every tile: the upright frames fit the whole plus, the leaning ones centre the icon
	const upright = '-560 -64 1120 1120';
	const leaning = '-260 -260 1120 1120';

	// the original pencil sketch (src/lib/assets/sketch.webp), shown on request; without the file the button is left out
	const sketches = import.meta.glob('../assets/sketch.{jpg,jpeg,png,webp,avif}', {
		eager: true,
		query: '?url',
		import: 'default'
	}) as Record<string, string>;
	const sketch = Object.values(sketches)[0];
	let sketchDialog = $state<HTMLDialogElement>();

	const specs: [string, string][] = [
		['Drawing', `${SIZE} × ${SIZE}`],
		['Angle', `${deg}° on all four slanted edges`],
		['Split', `${SPLIT} : ${lower}  (${Math.round((SPLIT / SIZE) * 100)} : ${Math.round((lower / SIZE) * 100)})`],
		['Steps', `five of 120 across ${SIZE}: 0, 120, 240, 360, 480, 600`],
		['Corners', `two 120° outer corners, cut back ${trim}, radius ≈ ${r}`],
		['Colours', '#111111 on light, #FAFAFA on dark'],
		['In Llama Sans', 'U+E000, cap-height tall on the baseline'],
		['Source', 'ggml-org/llama.brand · CC BY-NC 4.0']
	];
</script>

{#snippet icon(fill = 'var(--l-shape)')}
	{#each PATHS as d, i (i)}<path {d} {fill} />{/each}
{/snippet}

{#snippet panel(title: string, caption: string, body: Snippet)}
	<figure class="panel">
		<svg viewBox="-60 -60 720 720" role="img" aria-label={title}>{@render body()}</svg>
		<figcaption><strong>{title}</strong>{caption}</figcaption>
	</figure>
{/snippet}


{#snippet stage(n: string, title: string, caption: string, view: string, body: Snippet)}
	<figure class="panel stage">
		<span class="step">{n}</span>
		<svg viewBox={view} role="img" aria-label={title}>{@render body()}</svg>
		<figcaption><strong>{title}</strong>{caption}</figcaption>
	</figure>
{/snippet}

<div class="logo">
	<section class="hero" aria-label="Construction">
		<!-- pointer and tap highlighting is a shortcut; the legend buttons below give the same to keyboards and screen readers -->
		<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
		<svg
			viewBox={view}
			role="img"
			aria-label={done ? 'Blueprint of the Llama icon with its construction lines and dimensions' : `Animation: the + of C++ becomes the Llama icon and then its blueprint. Now: ${originSteps[step].name}`}
			class:focused={done && active}
			class:animating={!done}
			onpointerover={(e) => {
				if (!done) return;
				stopTour();
				if (e.pointerType === 'mouse') hovered = featureAt(e) ?? null;
			}}
			onpointerleave={() => (hovered = null)}
			onclick={(e) => {
				if (!done) return;
				stopTour();
				const f = featureAt(e);
				if (f) pin(f);
				else pinned = null;
			}}
		>
			<defs>
				<pattern id="bp-minor" width="20" height="20" patternUnits="userSpaceOnUse">
					<path d="M20 0H0V20" class="grid-minor" />
				</pattern>
				<pattern id="bp-major" width="120" height="120" patternUnits="userSpaceOnUse">
					<path d="M120 0H0V120" class="grid-major" />
				</pattern>
			</defs>
			<g style:opacity={fade.grid}>
				<rect x={box[0]} y={box[1]} width={box[2] - box[0]} height={box[3] - box[1]} fill="url(#bp-minor)" />
				<rect x={box[0]} y={box[1]} width={box[2] - box[0]} height={box[3] - box[1]} fill="url(#bp-major)" />
			</g>

			<g style:opacity={fade.lines}>
			{#each lines as { a, b, f }, i (i)}
				<g data-f={f} class:on={f && active === f} class:static={!f}>
					<line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} class="guide" />
					<line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} class="hit" />
				</g>
			{/each}
			{#each corners as c, i (i)}
				<g data-f="corners" class:on={active === 'corners'}>
					<circle cx={c.centre[0]} cy={c.centre[1]} r={c.r} class="guide" />
					<circle cx={c.centre[0]} cy={c.centre[1]} r={c.r} class="hit" />
					<circle cx={c.centre[0]} cy={c.centre[1]} r="4" class="joint" />
				</g>
			{/each}
			</g>
			<g style:opacity={fade.parts}>
			{#each [['lower', PATHS[0]], ['upper', PATHS[1]]] as [f, d] (f)}
				<path {d} class="part" data-f={f} class:on={active === f} />
			{/each}
			</g>
			<!-- the origin animation, drawn into this same drawing until the blueprint takes over -->
			{#if !done}<Morph {t} />{/if}

			<!-- dimensions -->
			<g style:opacity={fade.dims}>
			{#each dims as d, i (i)}
				<g class="dimension" data-f={d.f} class:on={d.f && active === d.f} class:static={!d.f}>
					<line x1={d.a[0]} y1={d.a[1]} x2={d.b[0]} y2={d.b[1]} />
					<line x1={d.a[0]} y1={d.a[1]} x2={d.b[0]} y2={d.b[1]} class="hit" />
					{#each [d.a, d.b] as p, j (j)}
						<line x1={p[0] - d.t[0]} y1={p[1] - d.t[1]} x2={p[0] + d.t[0]} y2={p[1] + d.t[1]} />
					{/each}
					<text x={d.at[0]} y={d.at[1]} text-anchor="middle" transform={d.rot ? `rotate(-90 ${d.at[0]} ${d.at[1]})` : undefined}>{d.label}</text>
				</g>
			{/each}
			<g data-f="angle" class:on={active === 'angle'}>
				<path d="M60 {SPLIT} A60 60 0 0 0 30 {SPLIT - 52}" class="dimension-arc" />
				<text x="72" y={SPLIT - 18} class="bp-label">{deg}°</text>
			</g>
			{#each corners as c, i (i)}
				<text x={c.centre[0] + (i ? 22 : -22)} y={c.centre[1] + (i ? 30 : -18)} text-anchor={i ? 'start' : 'end'} class="bp-label" data-f="corners" class:on={active === 'corners'}>R {r}</text>
			{/each}

			</g>

			<!-- title block -->
			<g class="title-block" transform="translate(620 600)" style:opacity={fade.title}>
				<rect width="280" height="140" />
				<line x1="0" y1="44" x2="280" y2="44" />
				<line x1="0" y1="92" x2="280" y2="92" />
				{#each [93, 186] as x (x)}<line x1={x} y1="92" x2={x} y2="140" />{/each}
				<text x="12" y="30" class="bp-title">LLAMA · ICON</text>
				<text x="12" y="74" class="bp-label">PLUS + L → BOLT</text>
				{#each [['ANGLE', `${Math.round(+deg)}°`, 'angle'], ['GRID', '120', 'steps'], ['SPLIT', `${SPLIT}:${SIZE - SPLIT}`, 'split']] as [k, val, f], n (k)}
					<g data-f={f} class:on={active === f}>
						<rect x={n * 93} y="92" width="93" height="48" class="hit-area" />
						<text x={n * 93 + 10} y="112" class="bp-small">{k}</text>
						<text x={n * 93 + 10} y="130" class="bp-label">{val}</text>
					</g>
				{/each}
			</g>
		</svg>
		<div class="legend">
			<div class="bar">
				<button type="button" class="play" onclick={() => (playing ? pause() : play())} aria-label={playing ? 'Pause' : done ? 'Replay the origin' : 'Play'}>
					{#if playing}
						<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" /></svg>
					{:else if done}
						<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3a5 5 0 1 0 5 5h-1.6A3.4 3.4 0 1 1 8 4.6V7l3.5-3.2L8 .6z" /></svg>
					{:else}
						<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5z" /></svg>
					{/if}
				</button>
				<input type="range" min="0" max={END} step="0.01" value={t} oninput={(e) => seek(+e.currentTarget.value)} aria-label="Position in the origin animation" />
			</div>
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div class="chips" class:idle={!done} inert={!done} role="group" aria-label="Highlight a part of the drawing" onpointerover={stopTour} onfocusin={stopTour}>
				{#each features as x (x.f)}
					<button
						type="button"
						aria-pressed={pinned === x.f}
						class:lit={active === x.f}
						onpointerenter={(e) => e.pointerType === 'mouse' && (hovered = x.f)}
						onpointerleave={() => (hovered = null)}
						onfocus={() => (hovered = x.f)}
						onblur={() => (hovered = null)}
						onclick={() => pin(x.f)}
					>{x.name}</button>
				{/each}
			</div>
			<p class="caption" aria-live="polite">
				{#if !done}<strong>{stepNumber(step)}{originSteps[step].name}.</strong> {originSteps[step].note}{:else if current}<strong>{current.name}.</strong> {current.note}{:else}Hover or tap any part of the drawing, or pick one here.{/if}
			</p>
		</div>
	</section>

	<header class="head">
		<span class="kicker">Llama · the icon</span>
		<h2>Two blades, one angle</h2>
		<p>
			The Llama icon is two slanted blades that meet at a single point. Every slanted edge runs at exactly {deg}°,
			the blades split the height {Math.round((SPLIT / SIZE) * 100)} to {Math.round((lower / SIZE) * 100)}, and only
			the two outer corners are softened.
		</p>
	</header>


	<section class="origin" aria-labelledby="origin-title">
		<header class="head">
			<span class="kicker">Where it comes from</span>
			<h2 id="origin-title">Plus, L, bolt</h2>
			<p>
				It begins with the + of C++, the language llama.cpp is written in. The icon started as a pencil sketch of that plus drawn into an L. Stand the blades upright and it is still
				there: the tall blade is the top arm of the +, the foot is its right arm, and the corner they would share is
				left out, so the two meet at a single point. Lean it 30° and a lightning bolt fits it exactly; soften two corners, and you have the mark.
			</p>
			{#if sketch}
				<button type="button" class="sketch-open" onclick={() => sketchDialog?.showModal()}>View the original sketch</button>
			{/if}
		</header>
		{#if sketch}
			<dialog class="sketch" bind:this={sketchDialog} closedby="any" aria-label="The original pencil sketch">
				<img src={sketch} alt="A sketchbook page in pencil: a slanted plus, the same plus with its top and right arms shaded, the two-blade icon in a rounded square, an upright plus with two arms shaded, L shapes built on a grid and an L drawn in perspective" />
				<form method="dialog"><button class="sketch-close">Close</button></form>
			</dialog>
		{/if}
		<div class="stages">
			{#snippet s1()}
				{#each plus as d, i (i)}<path {d} class="cell" />{/each}
			{/snippet}
			{@render stage('01', 'Plus', `A plus with the icon’s own arms: 240 wide upright, ${lower} deep across.`, upright, s1)}

			{#snippet s2()}
				{#each plus as d, i (i)}<path {d} class="ghost" />{/each}
				<path d="{rect(arm.top)}{rect(arm.centre)}{rect(arm.right)}" fill="var(--l-shape)" />
			{/snippet}
			{@render stage('02', 'L', 'Keep the top arm, the centre and the right arm: an L inside the +.', upright, s2)}

			{#snippet s3()}
				{#each plus as d, i (i)}<path {d} class="ghost" />{/each}
				{#each parts as d, i (i)}<path {d} fill="var(--l-shape)" />{/each}
				<path d={rect(arm.centre)} class="lifted" />
				<circle cx="120" cy={SPLIT} r="14" class="joint" />
			{/snippet}
			{@render stage('03', 'Open the corner', 'Lift out the centre block the + and the L share. Stem and foot now touch at one point.', upright, s3)}

			{#snippet s4()}
				{#each parts as d, i (i)}<path {d} class="lifted" />{/each}
				<g transform={sheared}>{#each parts as d, i (i)}<path {d} fill="var(--l-shape)" />{/each}</g>
				<circle cx="240" cy={SPLIT} r="14" class="joint" />
			{/snippet}
			{@render stage('04', 'Lean', `Slant it 30° from upright on the baseline: every edge now runs at ${deg}°.`, leaning, s4)}

			{#snippet sBolt()}
				<g transform={sheared}>{#each parts as d, i (i)}<path {d} class="cell-outline" />{/each}</g>
				<path d={LIGHTNING} class="strike" />
			{/snippet}
			{@render stage('05', 'Bolt', 'Cut the blade along its diagonal and turn that half about the joint: a lightning bolt inside the L. Speed, which is what llama.cpp is about.', leaning, sBolt)}

			{#snippet s5()}
				<g transform={sheared}>{#each parts as d, i (i)}<path {d} class="ghost" />{/each}</g>
				{@render icon()}
				{#each corners as c, i (i)}<circle cx={c.centre[0]} cy={c.centre[1]} r={c.r} class="guide" />{/each}
			{/snippet}
			{@render stage('06', 'Soften', 'Round only the two outer corners. That is the Llama icon.', leaning, s5)}
		</div>
	</section>

	<div class="panels">
		{#snippet blades()}
			<path d={PATHS[1]} fill="var(--l-shape)" />
			<path d={PATHS[0]} fill="var(--l-shape-2)" />
			<text x="150" y="250" class="note on-shape">upper blade</text>
			<text x="300" y="520" class="note on-shape">lower blade</text>
		{/snippet}
		{@render panel('Two blades', 'A tall blade and a short foot, offset to the right, touching at one point.', blades)}

		{#snippet sixty()}
			{@render icon('var(--l-faint)')}
			{#each [[0, SPLIT], [240, SPLIT], [120, SIZE]] as [x, y], i (i)}
				<path d="M{x + 80} {y} A80 80 0 0 0 {x + 40} {y - 69.3}" class="arc" />
				<text x={x + 92} y={y - 26} class="note">60°</text>
			{/each}
			{#each [edges.upperLeft, edges.shared, edges.lowerRight] as [a, b], i (i)}
				<line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} class="hi" />
			{/each}
		{/snippet}
		{@render panel('60° everywhere', `All four slanted edges lean at ${deg}°: the blades are parallel parallelograms.`, sixty)}

		{#snippet shared()}
			{@render icon('var(--l-faint)')}
			<line x1="466.154" y1="0" x2="120" y2="600" class="hi" />
			<circle cx="240" cy={SPLIT} r="12" class="joint" />
			<text x="270" y={SPLIT + 10} class="note">240, {SPLIT}</text>
		{/snippet}
		{@render panel('One diagonal', 'The upper blade’s right edge and the foot’s left edge are the same line, through the joint.', shared)}

		{#snippet split()}
			{@render icon('var(--l-faint)')}
			<line x1="-40" y1={SPLIT} x2="640" y2={SPLIT} class="hi" />
			<line x1="-30" y1="0" x2="-30" y2={SPLIT} class="dim" />
			<line x1="-30" y1={SPLIT} x2="-30" y2={SIZE} class="dim" />
			<text x="-20" y={SPLIT / 2} class="note">{SPLIT}</text>
			<text x="-20" y={SPLIT + lower / 2 + 10} class="note">{lower}</text>
		{/snippet}
		{@render panel('The split', `${SPLIT} above, ${lower} below: close to two thirds to one third.`, split)}

		{#snippet steps()}
			{@render icon('var(--l-faint)')}
			{#each STEPS as x (x)}
				<line x1={x} y1="-40" x2={x} y2="616" class="hi" />
				<text {x} y="652" text-anchor="middle" class="note">{x}</text>
			{/each}
		{/snippet}
		{@render panel('Steps of 120', `Five steps of 120 span the ${SIZE}: the feet, the joint and the foot’s corner all land on them.`, steps)}

		{#snippet round()}
			{@render icon('var(--l-faint)')}
			{#each corners as c, i (i)}
				<circle cx={c.centre[0]} cy={c.centre[1]} r={c.r} class="hi" />
				<line x1={c.sharp[0]} y1={c.sharp[1]} x2={c.tangentFlat[0]} y2={c.tangentFlat[1]} class="dim" />
				<circle cx={c.sharp[0]} cy={c.sharp[1]} r="8" class="joint" />
			{/each}
		{/snippet}
		{@render panel('Soft outer corners', `Only the two 120° outer corners round off: cut back ${trim}, on a circle of radius ≈ ${r}.`, round)}
	</div>

	<section class="type" aria-label="The icon in Llama Sans">
		<span class="kicker">In Llama Sans · U+E000</span>
		<p class="lockup display">{''} llama.cpp</p>
		<p class="lockup ui"><span class="pill">{''} Open in Llama</span><span class="pill ghost">{''} llama.app</span></p>
		<p class="lockup text">
			The icon sits on the baseline and reaches exactly the cap height, so it lines up with capitals in a line of
			text: {''} Llama, {''} LLAMA.CPP.
		</p>
	</section>

	<dl class="specs">
		{#each specs as [k, v] (k)}<div><dt>{k}</dt><dd>{v}</dd></div>{/each}
	</dl>
</div>

<style>
	.logo {
		/* grayscale after the brand: black icon on light grey in light mode, white icon on near-black in
		   dark mode; construction lines in a mid grey that reads over both the icon and the ground */
		--l-bg: #ededed;
		--l-shape: #111111;
		--l-shape-2: #6b6b6b;
		--l-faint: rgba(17, 17, 17, 0.16);
		--l-line: #9a9a9a;
		--l-ink: #111111;
		--l-muted: #5f5f5f;
		--l-panel: rgba(255, 255, 255, 0.65);
		--l-rule: rgba(17, 17, 17, 0.14);
		--l-bolt: #f2b400;
		/* in light mode the bolt is solid, so it reads crisply inside the black L (see-through yellow over black turns olive) */
		--l-bolt-alpha: 1;
		--l-bolt-tint: 0;
		--l-paper: #f6f6f6;
		--l-grid: rgba(17, 17, 17, 0.05);
		--l-grid-major: rgba(17, 17, 17, 0.13);
		display: grid;
		gap: 40px;
		padding: clamp(16px, 4vw, 48px);
		border-radius: 16px;
		background: var(--l-bg);
		color: var(--l-ink);
	}
	@media (prefers-color-scheme: dark) {
		:global(:root:not([data-theme='light'])) .logo {
			--l-bg: #141414;
			--l-shape: #fafafa;
			--l-shape-2: #9e9e9e;
			--l-faint: rgba(250, 250, 250, 0.18);
			--l-line: #6f6f6f;
			--l-ink: #fafafa;
			--l-muted: #a3a3a3;
			--l-panel: rgba(255, 255, 255, 0.05);
			--l-rule: rgba(250, 250, 250, 0.14);
			--l-bolt: #ffd426;
			--l-bolt-alpha: 0.85;
			--l-bolt-tint: 0.3;
			--l-paper: #1a1a1a;
			--l-grid: rgba(250, 250, 250, 0.05);
			--l-grid-major: rgba(250, 250, 250, 0.13);
		}
	}
	:global(:root[data-theme='dark']) .logo {
		--l-bg: #141414;
		--l-shape: #fafafa;
		--l-shape-2: #9e9e9e;
		--l-faint: rgba(250, 250, 250, 0.18);
		--l-line: #6f6f6f;
		--l-ink: #fafafa;
		--l-muted: #a3a3a3;
		--l-panel: rgba(255, 255, 255, 0.05);
		--l-rule: rgba(250, 250, 250, 0.14);
		--l-bolt: #ffd426;
		--l-bolt-alpha: 0.85;
		--l-bolt-tint: 0.3;
		--l-paper: #1a1a1a;
		--l-grid: rgba(250, 250, 250, 0.05);
		--l-grid-major: rgba(250, 250, 250, 0.13);
	}
	.hero {
		border: 1px solid var(--l-rule);
		border-radius: 12px;
		overflow: hidden;
		background: var(--l-paper);
	}
	.grid-minor {
		fill: none;
		stroke: var(--l-grid);
		stroke-width: 1;
		vector-effect: non-scaling-stroke;
	}
	.grid-major {
		fill: none;
		stroke: var(--l-grid-major);
		stroke-width: 1;
		vector-effect: non-scaling-stroke;
	}
	.part {
		fill: var(--l-faint);
		stroke: var(--l-ink);
		stroke-width: 2;
		vector-effect: non-scaling-stroke;
	}
	.dimension line,
	.dimension-arc,
	.title-block rect,
	.title-block line {
		fill: none;
		stroke: var(--l-muted);
		stroke-width: 1;
		vector-effect: non-scaling-stroke;
	}
	.dimension text,
	.bp-label,
	.bp-small,
	.bp-title {
		font: 500 15px var(--mono);
		letter-spacing: 0.06em;
		fill: var(--l-muted);
	}
	.bp-small {
		font-size: 11px;
	}
	.bp-title {
		font: 700 20px 'Llama Sans Display', var(--body);
		letter-spacing: 0;
		fill: var(--l-ink);
	}
	/* blueprint highlighting: with a part active, everything tagged dims except that part's idea */
	[data-f] {
		cursor: pointer;
		transition: opacity 200ms ease-out;
	}
	[data-f] :is(line, circle, path, text),
	[data-f]:is(path, text) {
		transition: stroke 200ms ease-out, fill 200ms ease-out, fill-opacity 200ms ease-out, stroke-width 200ms ease-out;
	}
	.static {
		transition: opacity 200ms ease-out;
	}
	.hero svg.focused [data-f]:not(.on),
	.hero svg.focused .static {
		opacity: 0.14;
	}
	.hit {
		fill: none;
		stroke: transparent;
		stroke-width: 16;
		vector-effect: non-scaling-stroke;
		pointer-events: stroke;
	}
	.hit-area {
		fill: transparent;
	}
	.on > .guide {
		stroke: var(--l-ink);
		stroke-width: 1.6;
		stroke-dasharray: none;
	}
	.part.on {
		fill: var(--l-shape-2);
		fill-opacity: 0.6;
		stroke-width: 2.5;
	}
	.on .joint {
		fill: var(--l-ink);
	}
	.dimension.on line,
	.on .dimension-arc {
		stroke: var(--l-ink);
	}
	.dimension.on text,
	.on .bp-label,
	.on .bp-small,
	.bp-label.on {
		fill: var(--l-ink);
	}
	.hero svg.animating {
		cursor: default;
	}
	.bar {
		display: grid;
		grid-template-columns: auto 1fr;
		align-items: center;
		gap: 12px;
	}
	.play {
		display: grid;
		place-items: center;
		width: 32px;
		height: 32px;
		padding: 0;
		border: 0;
		border-radius: 50%;
		background: var(--l-ink);
		color: var(--l-bg);
		cursor: pointer;
	}
	.play svg {
		width: 13px;
		height: 13px;
		fill: currentColor;
	}
	.play:focus-visible {
		outline: 2px solid var(--l-ink);
		outline-offset: 2px;
	}
	.bar input[type='range'] {
		width: 100%;
		accent-color: var(--l-ink);
	}
	.chips.idle {
		opacity: 0.4;
	}
	.chips {
		transition: opacity 300ms ease-out;
	}
	.legend {
		display: grid;
		gap: 10px;
		padding: 14px 16px 16px;
		border-top: 1px solid var(--l-rule);
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}
	.chips button {
		padding: 0.35em 0.8em;
		border: 0;
		border-radius: 999px;
		background: none;
		box-shadow: inset 0 0 0 1px var(--l-rule);
		color: var(--l-muted);
		font: 500 13px / normal 'Llama Sans UI', var(--body);
		cursor: pointer;
		transition: background-color 160ms ease, color 160ms ease;
	}
	.chips button.lit {
		box-shadow: inset 0 0 0 1px var(--l-ink);
		color: var(--l-ink);
	}
	.chips button[aria-pressed='true'] {
		background: var(--l-ink);
		color: var(--l-bg);
	}
	.chips button:focus-visible {
		outline: 2px solid var(--l-ink);
		outline-offset: 2px;
	}
	.caption {
		margin: 0;
		min-height: 2.9em;
		font: 400 14px / 1.45 'Llama Sans Text', var(--body);
		color: var(--l-muted);
	}
	.caption strong {
		color: var(--l-ink);
		font-weight: 600;
	}
	.hero svg {
		display: block;
		width: 100%;
		height: auto;
		max-height: 80vh;
	}
	.guide {
		stroke: var(--l-line);
		stroke-width: 1;
		stroke-dasharray: 6 4;
		fill: none;
		vector-effect: non-scaling-stroke;
	}
	.joint {
		fill: var(--l-line);
	}
	.head {
		display: grid;
		gap: 10px;
		max-width: 62ch;
	}
	.kicker {
		font: 500 12px var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--l-muted);
	}
	h2 {
		margin: 0;
		font: 700 clamp(32px, 5vw, 56px) / normal 'Llama Sans Display', var(--body);
	}
	.head p {
		margin: 0;
		color: var(--l-muted);
		font: 400 17px / normal 'Llama Sans Text', var(--body);
	}
	.sketch-open,
	.sketch-close {
		justify-self: start;
		padding: 0.5em 1em;
		border: 0;
		border-radius: 8px;
		background: none;
		box-shadow: inset 0 0 0 1px var(--l-ink);
		color: var(--l-ink);
		font: 500 15px / normal 'Llama Sans UI', var(--body);
		cursor: pointer;
	}
	.sketch-open:focus-visible,
	.sketch-close:focus-visible {
		outline: 2px solid var(--l-ink);
		outline-offset: 2px;
	}
	.sketch {
		max-width: min(92vw, 900px);
		max-height: 92vh;
		padding: 12px;
		border: 0;
		border-radius: 12px;
		background: var(--l-bg);
		color: var(--l-ink);
	}
	.sketch::backdrop {
		background: rgba(0, 0, 0, 0.6);
	}
	.sketch img {
		display: block;
		max-width: 100%;
		max-height: calc(92vh - 80px);
		margin: 0 auto;
		border-radius: 6px;
	}
	.sketch form {
		display: flex;
		justify-content: flex-end;
		margin-top: 10px;
	}
	.origin {
		display: grid;
		gap: 20px;
	}
	.stages {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 16px;
	}
	.stage {
		position: relative;
	}
	.step {
		font: 500 11px var(--mono);
		letter-spacing: 0.08em;
		color: var(--l-muted);
	}
	.cell-outline {
		fill: none;
		stroke: var(--l-ink);
		stroke-width: 2;
		vector-effect: non-scaling-stroke;
	}
	.strike {
		fill: var(--l-bolt);
		fill-opacity: var(--l-bolt-alpha);
	}
	.cell {
		fill: var(--l-faint);
		stroke: var(--l-ink);
		stroke-width: 2.5;
		vector-effect: non-scaling-stroke;
	}
	.ghost {
		fill: none;
		stroke: var(--l-line);
		stroke-width: 1.5;
		vector-effect: non-scaling-stroke;
	}
	.lifted {
		fill: none;
		stroke: var(--l-ink);
		stroke-width: 1.5;
		stroke-dasharray: 5 5;
		vector-effect: non-scaling-stroke;
	}
	.panels {
		/* six panels: 3 x 2 on wide screens, 2 x 3 on tablets, one column on phones */
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 16px;
	}
	@media (max-width: 860px) {
		.panels {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
	@media (max-width: 520px) {
		.panels {
			grid-template-columns: minmax(0, 1fr);
		}
	}
	.panel {
		margin: 0;
		display: grid;
		gap: 10px;
		align-content: start;
		min-width: 0;
		padding: 14px;
		border-radius: 12px;
		background: var(--l-panel);
	}
	.panel svg {
		display: block;
		width: 100%;
		height: auto;
	}
	.panel figcaption {
		display: grid;
		gap: 2px;
		font: 400 14px / normal 'Llama Sans Text', var(--body);
		color: var(--l-muted);
	}
	.panel strong {
		color: var(--l-ink);
		font: 600 15px / normal 'Llama Sans UI', var(--body);
	}
	.hi {
		stroke: var(--l-ink);
		stroke-width: 2.5;
		fill: none;
		vector-effect: non-scaling-stroke;
	}
	.dim {
		stroke: var(--l-ink);
		stroke-width: 1.5;
		stroke-dasharray: 4 4;
		vector-effect: non-scaling-stroke;
	}
	.arc {
		stroke: var(--l-ink);
		stroke-width: 2;
		fill: none;
		vector-effect: non-scaling-stroke;
	}
	.note {
		font: 500 30px 'Llama Sans UI', var(--body);
		fill: var(--l-ink);
	}
	.note.on-shape {
		fill: var(--l-bg);
	}
	.type {
		display: grid;
		gap: 18px;
	}
	.lockup {
		margin: 0;
	}
	.display {
		font: 700 clamp(48px, 9vw, 112px) / normal 'Llama Sans Display', var(--body);
	}
	.ui {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
	}
	.pill {
		display: inline-flex;
		align-items: center;
		padding: 0.5em 1em;
		border-radius: 8px;
		background: var(--l-ink);
		color: var(--l-bg);
		font: 500 15px / normal 'Llama Sans UI', var(--body);
	}
	.pill.ghost {
		background: none;
		color: var(--l-ink);
		box-shadow: inset 0 0 0 1px var(--l-ink);
	}
	.text {
		max-width: 62ch;
		font: 400 17px / normal 'Llama Sans Text', var(--body);
	}
	.specs {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
		gap: 14px 24px;
		margin: 0;
	}
	.specs div {
		display: grid;
		gap: 3px;
		min-width: 0;
		padding-top: 10px;
		border-top: 1px solid var(--l-rule);
	}
	.specs dt {
		font: 500 11px var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--l-muted);
	}
	.specs dd {
		margin: 0;
		font: 400 15px / normal 'Llama Sans UI', var(--body);
	}
</style>
