<script lang="ts">
	import { specimen, fallback } from '#lib/specimen.ts';
	import Controls from '#lib/components/Controls.svelte';
	import GlyphGrid from '#lib/components/GlyphGrid.svelte';
	import ShowcaseDisplay from '#lib/components/ShowcaseDisplay.svelte';
	import ShowcaseUI from '#lib/components/ShowcaseUI.svelte';
	import ShowcaseText from '#lib/components/ShowcaseText.svelte';
	import Tester from '#lib/components/Tester.svelte';
	import Notes from '#lib/components/Notes.svelte';
	import CompareSwitch from '#lib/components/CompareSwitch.svelte';

	const { metrics, axis, styles, waterfall, variants, glyphCount } = specimen;

	let weight = $state(styles[0].weight);
	let variant = $state(variants[0]); // opens on the first version (Display)
	let comparing = $state(false);
	let size = $state(64);
	let tracking = $state(0);
	let guides = $state(false);

	// live text follows any weight; the glyph grid shows the nearest named weight
	const named = $derived(
		styles.reduce((a, s) => (Math.abs(s.weight - weight) < Math.abs(a.weight - weight) ? s : a)).weight
	);
	const variantNotes: Record<string, string> = {
		Text: 'Articles and long reading. Switch to UI or Display at the top (or press V).',
		UI: 'Controls and small interface text. Turn on line boxes in the bar to see the alignment.',
		Display: 'Banners, headlines and large type. Switch to Text or UI at the top (or press V).'
	};
	// comparing swaps every version for the same version of the earlier build
	const family = $derived(`"Llama Sans ${comparing ? 'Prev ' : ''}${variant}", ${fallback}`);

	function onkeydown(e: KeyboardEvent) {
		const t = e.target as HTMLElement;
		if (e.metaKey || e.ctrlKey || e.altKey) return;
		const typing = t.isContentEditable || (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) &&
			!['radio', 'range', 'checkbox'].includes((t as HTMLInputElement).type));
		if (typing) return;
		const key = e.key.toLowerCase();
		if (key === 'v') variant = variants[(variants.indexOf(variant) + 1) % variants.length];
		if (key === 'b' && specimen.compare) comparing = !comparing;
	}
</script>

<svelte:window {onkeydown} />

<div class="wrap" style:--w={weight} style:--display={family}>
	<header>
		<div class="top">
			<span class="label">Draft 0.6 · variable {axis.min}–{axis.max} · {glyphCount} glyphs</span>
			<span class="label">Llama family · Sans</span>
		</div>
		<h1>Llama Sans <span class="version">{variant}</span></h1>
		<p class="lede">
			The sans of the Llama family, with Mono and Serif to follow. A neo-grotesk with an even stroke, round bowls and
			open, angle-cut terminals, in three variable fonts from {axis.min} to {axis.max} that share every outline: Display
			for headlines, UI for interfaces, Text for prose.
		</p>
		<dl class="metrics">
			<div><dt>UPM</dt><dd>{metrics.upm}</dd></div>
			<div><dt>Cap height</dt><dd>{metrics.cap}</dd></div>
			<div><dt>x-height</dt><dd>{metrics.x}</dd></div>
			<div><dt>Ascender</dt><dd>{metrics.asc}</dd></div>
			<div><dt>Descender</dt><dd>{metrics.dsc}</dd></div>
			<div><dt>Weight axis</dt><dd>{axis.min}–{axis.max}</dd></div>
			<div><dt>Stems {styles.map((s) => s.weight).join(' · ')}</dt><dd>{styles.map((s) => s.stem).join(' · ')}</dd></div>
			<div><dt>Display</dt><dd>tracking −26 · kerning 115% · line 1.15</dd></div>
			<div><dt>UI</dt><dd>tracking −4 · kerning 105% · line 1.25, cap-centred</dd></div>
			<div><dt>Text</dt><dd>tracking +10 · kerning 85% · line 1.5</dd></div>
		</dl>
	</header>

	<Controls bind:weight bind:variant bind:size bind:tracking bind:guides />

	<Tester {glyphCount} {size} {tracking} />

	<section class="showcase" aria-label="In use">
		<div class="showcase-head">
			<span class="label">In use · Llama Sans {variant}</span>
			<span class="showcase-note">{variantNotes[variant]}</span>
		</div>
		{#if variant === 'Display'}
			<ShowcaseDisplay />
		{:else if variant === 'UI'}
			<ShowcaseUI {glyphCount} {guides} />
		{:else}
			<ShowcaseText />
		{/if}
	</section>

	<section class="waterfall" aria-label="Weights">
		<span class="label">Weights</span>
		{#each waterfall as w (w.weight)}
			<div class="wrow">
				<span class="label">{w.weight} · {w.name}</span>
				<p style:font-weight={w.weight}>Sphinx of black quartz, judge my vow 2026</p>
			</div>
		{/each}
	</section>

	<section class="setting" aria-label="Sample setting">
		<span class="label">Setting</span>
		<p class="s1">Hamburgefonstiv 2026</p>
		<p class="s2">Sphinx of black quartz, judge my vow. 0123456789</p>
	</section>

	<GlyphGrid weight={named} {comparing} />

	<Notes />

	{#if specimen.compare}
		<CompareSwitch bind:comparing labels={specimen.compare.labels} />
	{/if}
</div>

<style>
	.wrap {
		max-width: 1180px;
		margin: 0 auto;
		padding-block: 40px 80px;
		padding-left: max(16px, env(safe-area-inset-left, 0px));
		padding-right: max(16px, env(safe-area-inset-right, 0px));
		display: grid;
		gap: 56px;
	}
	header {
		display: grid;
		gap: 20px;
	}
	.top {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 12px;
		align-items: baseline;
	}
	h1 {
		margin: 0;
		font: var(--w) clamp(56px, 12vw, 148px) / 0.9 var(--display);
		letter-spacing: -0.01em;
		text-wrap: balance;
	}
	h1 .version {
		display: block; /* the version always sits on its own line */
		color: var(--muted);
	}
	.lede {
		max-width: 62ch;
		margin: 0;
		color: var(--muted);
		font-size: 17px;
	}
	.metrics {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 28px;
		margin: 0;
		padding: 14px 0 0;
		border-top: 1px solid var(--rule);
	}
	.metrics div {
		display: grid;
		gap: 2px;
	}
	.metrics dt {
		font: 500 11px var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.metrics dd {
		margin: 0;
		font: 400 15px var(--mono);
		font-variant-numeric: tabular-nums;
	}
	.waterfall,
	.showcase,
	.setting {
		display: grid;
		gap: 12px;
	}
	.showcase {
		gap: 18px;
	}
	.showcase-head {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 6px 16px;
		align-items: baseline;
	}
	.showcase-note {
		font-size: 13px;
		color: var(--muted);
	}
	.wrow {
		display: grid;
		gap: 2px;
	}
	.wrow p {
		margin: 0;
		font-family: var(--display);
		font-size: clamp(26px, 4.4vw, 52px);
		line-height: 1.1;
		overflow-wrap: anywhere;
	}
	.setting p {
		margin: 0;
		font-family: var(--display);
		font-weight: var(--w);
		overflow-wrap: anywhere;
	}
	.s1 {
		font-size: clamp(34px, 6vw, 76px);
		line-height: 1.02;
	}
	.s2 {
		font-size: clamp(20px, 3vw, 34px);
		line-height: 1.2;
		color: var(--muted);
	}
</style>
