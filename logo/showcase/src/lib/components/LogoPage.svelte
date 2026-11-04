<!-- The Llama icon taken apart: its construction lines, then each rule that shapes it. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { PATHS, SIZE, SPLIT, edges, corners, angle, extend, type Pt } from '#lib/logo.ts';

	const box: [number, number, number, number] = [-320, -160, 920, 760];
	const vb = `${box[0]} ${box[1]} ${box[2] - box[0]} ${box[3] - box[1]}`;

	// perpendicular to the 60° edges, through a point
	const sh = edges.shared;
	const dir: Pt = [sh[1][0] - sh[0][0], sh[1][1] - sh[0][1]];
	const perp = (p: Pt): [Pt, Pt] => [p, [p[0] - dir[1], p[1] + dir[0]]];

	const verticals = [0, 120, 240, corners[0].tangentFlat[0], corners[1].tangentFlat[0], 466.154, SIZE];
	const horizontals = [0, SPLIT, SIZE, corners[0].centre[1], corners[1].centre[1]];
	const lines: [Pt, Pt][] = [
		...verticals.map((x) => [[x, 0], [x, 1]] as [Pt, Pt]),
		...horizontals.map((y) => [[0, y], [1, y]] as [Pt, Pt]),
		edges.upperLeft,
		edges.shared,
		edges.lowerRight,
		perp([240, SPLIT]),
		perp([0, SPLIT]),
		perp([SIZE, SPLIT]),
		perp([120, SIZE]),
		perp([466.154, 0])
	].map(([a, b]) => extend(a, b, box));


	// blueprint dimensions: two end points, a tick offset, where the label sits
	type Dim = { a: Pt; b: Pt; t: Pt; at: Pt; label: string; rot?: boolean };
	const h = (y: number, x0: number, x1: number, label: string): Dim =>
		({ a: [x0, y], b: [x1, y], t: [0, 10], at: [(x0 + x1) / 2, y - 12], label });
	const v = (x: number, y0: number, y1: number, label: string): Dim =>
		({ a: [x, y0], b: [x, y1], t: [10, 0], at: [x - 12, (y0 + y1) / 2], label, rot: true });
	const dims: Dim[] = [
		h(-100, 0, SIZE, `${SIZE}`),
		h(-50, 226.15, 466.154, '240'),
		v(-100, 0, SPLIT, `${SPLIT}`),
		v(-100, SPLIT, SIZE, `${SIZE - SPLIT}`),
		v(-160, 0, SIZE, `${SIZE}`),
		h(690, 0, 120, '120'),
		h(690, 120, 240, '120'),
		h(690, 240, SIZE, `${SIZE - 240}`)
	];

	const deg = angle(...edges.upperLeft).toFixed(1);
	const lower = SIZE - SPLIT;
	const r = Math.round(corners[0].r);
	const trim = Math.round(corners[0].trim);


	// where it comes from: undo the lean and the icon is an upright + and L on a 120 grid. The upper blade is
	// the +'s top arm, the foot is its right arm, and the corner square they would share is left out.
	const lean = 1 / Math.tan(Math.PI / 3); // 30° from upright
	const sheared = `matrix(1 0 ${-lean} 1 ${SIZE * lean} 0)`; // pivots on the baseline, so the feet stay put
	const rect = ([u0, y0, u1, y1]: number[]) => `M${u0} ${y0}H${u1}V${y1}H${u0}Z`;
	const arm = {
		top: [-120, 0, 120, SPLIT],
		centre: [-120, SPLIT, 120, SIZE],
		right: [120, SPLIT, 480, SIZE],
		left: [-480, SPLIT, -120, SIZE],
		bottom: [-120, SIZE, 120, SIZE + lower]
	};
	const plus = Object.values(arm).map(rect);
	const parts = [rect(arm.top), rect(arm.right)];
	// a classic lightning bolt drawn on the icon's own 60° edges
	const bolt = 'M226.15 0H466.15L346 208H520L224.4 720L300 392H0Z';
	const upright = '-500 -96 1000 1000';
	const leaning = '-200 -200 1000 1000';

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
		['Steps', 'feet at x = 0, 120, 240'],
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
		<svg viewBox={vb} role="img" aria-label="Blueprint of the Llama icon with its construction lines and dimensions">
			<defs>
				<pattern id="bp-minor" width="20" height="20" patternUnits="userSpaceOnUse">
					<path d="M20 0H0V20" class="grid-minor" />
				</pattern>
				<pattern id="bp-major" width="120" height="120" patternUnits="userSpaceOnUse">
					<path d="M120 0H0V120" class="grid-major" />
				</pattern>
			</defs>
			<rect x={box[0]} y={box[1]} width={box[2] - box[0]} height={box[3] - box[1]} fill="url(#bp-minor)" />
			<rect x={box[0]} y={box[1]} width={box[2] - box[0]} height={box[3] - box[1]} fill="url(#bp-major)" />

			{#each lines as [a, b], i (i)}
				<line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} class="guide" />
			{/each}
			{#each corners as c, i (i)}
				<circle cx={c.centre[0]} cy={c.centre[1]} r={c.r} class="guide" />
				<circle cx={c.centre[0]} cy={c.centre[1]} r="4" class="joint" />
			{/each}
			{#each PATHS as d, i (i)}<path {d} class="part" />{/each}
			<circle cx="240" cy={SPLIT} r="6" class="joint" />

			<!-- dimensions -->
			{#each dims as d, i (i)}
				<g class="dimension">
					<line x1={d.a[0]} y1={d.a[1]} x2={d.b[0]} y2={d.b[1]} />
					{#each [d.a, d.b] as p, j (j)}
						<line x1={p[0] - d.t[0]} y1={p[1] - d.t[1]} x2={p[0] + d.t[0]} y2={p[1] + d.t[1]} />
					{/each}
					<text x={d.at[0]} y={d.at[1]} text-anchor="middle" transform={d.rot ? `rotate(-90 ${d.at[0]} ${d.at[1]})` : undefined}>{d.label}</text>
				</g>
			{/each}
			<path d="M60 {SPLIT} A60 60 0 0 0 30 {SPLIT - 52}" class="dimension-arc" />
			<text x="72" y={SPLIT - 18} class="bp-label">{deg}°</text>
			{#each corners as c, i (i)}
				<text x={c.centre[0] + (i ? 22 : -22)} y={c.centre[1] + (i ? 30 : -18)} text-anchor={i ? 'start' : 'end'} class="bp-label">R {r}</text>
			{/each}
			<text x="252" y={SPLIT + 26} class="bp-label">JOINT 240, {SPLIT}</text>

			<!-- title block -->
			<g class="title-block" transform="translate(620 600)">
				<rect width="280" height="140" />
				<line x1="0" y1="44" x2="280" y2="44" />
				<line x1="0" y1="92" x2="280" y2="92" />
				{#each [93, 186] as x (x)}<line x1={x} y1="92" x2={x} y2="140" />{/each}
				<text x="12" y="30" class="bp-title">LLAMA · ICON</text>
				<text x="12" y="74" class="bp-label">PLUS + L → BOLT</text>
				{#each [['ANGLE', `${Math.round(+deg)}°`], ['GRID', '120'], ['SPLIT', `${SPLIT}:${SIZE - SPLIT}`]] as [k, val], n (k)}
					<text x={n * 93 + 10} y="112" class="bp-small">{k}</text>
					<text x={n * 93 + 10} y="130" class="bp-label">{val}</text>
				{/each}
			</g>
		</svg>
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
				The icon started as a pencil sketch of a plus drawn into an L. Stand the blades upright and it is still
				there: the tall blade is the top arm of the +, the foot is its right arm, and the corner they would share is
				left out, so the two meet at a single point. A lightning bolt gives it its slant: lean it 30°, soften two corners, and you have the mark.
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
			{@render stage('01', 'Plus', 'Five blocks on a 120 grid: a centre and four arms.', upright, s1)}

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

			{#snippet sBolt()}
				{#each parts as d, i (i)}<path {d} class="lifted" />{/each}
				<path d={bolt} class="hi" />
			{/snippet}
			{@render stage('04', 'Bolt', 'Then a lightning bolt, for speed: it is what tips the upright stem and foot into a slant.', leaning, sBolt)}

			{#snippet s4()}
				{#each parts as d, i (i)}<path {d} class="lifted" />{/each}
				<g transform={sheared}>{#each parts as d, i (i)}<path {d} fill="var(--l-shape)" />{/each}</g>
				<circle cx="240" cy={SPLIT} r="14" class="joint" />
			{/snippet}
			{@render stage('05', 'Lean', `Slant it 30° from upright on the baseline: every edge now runs at ${deg}°.`, leaning, s4)}

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
			{#each [0, 120, 240] as x (x)}
				<line x1={x} y1="-40" x2={x} y2="640" class="hi" />
				<text x={x + 6} y="660" class="note">{x}</text>
			{/each}
		{/snippet}
		{@render panel('Steps of 120', 'The blade feet sit on a 120-unit step: 0, 120, 240.', steps)}

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
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
		gap: 16px;
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
