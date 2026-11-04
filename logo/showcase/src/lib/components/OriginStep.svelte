<!-- One step of where the icon comes from, as a tile: the name llama.cpp, the plus of its C++, the L inside it, the opened corner, the lean with
     the bolt inside it, and the softened corners. The caption is the children. With t (the origin animation's clock), the tile
     stays dimmed until the animation has drawn its step, and a click
     moves the clock to that step (bind:t). -->
<script lang="ts" module>
	export const ORIGIN_STEPS = ['name', 'plus', 'l', 'open', 'lean', 'soften'] as const;
	export type OriginStepName = (typeof ORIGIN_STEPS)[number];
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import Figure from './Figure.svelte';
	import { PATHS, SPLIT, corners } from '#lib/logo.ts';
	import { LIGHTNING, steps as originSteps, STEP, WORD } from '#lib/origin.ts';
	import { arm, plus, parts, rect, sheared } from '#lib/blueprint.ts';

	let {
		step,
		title,
		t = $bindable(),
		children
	}: { step: OriginStepName; title?: string; t?: number; children?: Snippet } = $props();

	const titles: Record<OriginStepName, string> = {
		name: 'llama.cpp',
		plus: 'Plus',
		l: 'L',
		open: 'Open the corner',
		lean: 'Lean',
		soften: 'Soften'
	};
	// one scale for every tile: the upright frames fit the whole plus, the leaning ones centre the icon; the name is
	// set in font units, centred on its ink
	const upright = '-560 -64 1120 1120';
	const leaning = '-260 -260 1120 1120';
	const views: Record<OriginStepName, string> = {
		name: '-200 -2680 4800 4800',
		plus: upright,
		l: upright,
		open: upright,
		lean: leaning,
		soften: leaning
	};
	const i = $derived(ORIGIN_STEPS.indexOf(step));
	// each tile is named after its step of the origin animation
	// a click shows the step drawn; the tile lights up then too, except the lean's, which lights up with the bolt's
	// strike that causes it
	const at = $derived(originSteps[STEP[titles[step]]].to);
	const litAt = $derived(step === 'lean' ? originSteps[STEP.Bolt].from : at);
	const lit = $derived(t === undefined || t >= litAt);
</script>

<Figure n={String(i + 1).padStart(2, '0')} title={title ?? titles[step]} view={views[step]} dim={!lit}
	onclick={t === undefined ? undefined : () => (t = at)}
	action="Show {title ?? titles[step]} in the animation"
	{children}
>
	{#snippet drawing()}
		{#if step === 'name'}
			<!-- "llama.cpp" in Llama Sans Display Bold, its .cpp in full ink: where the + comes from -->
			{#each WORD.layout as [ch, x], j (j)}
				<path
					d={WORD.glyphs[ch].d}
					transform="translate({x} 0) scale(1 -1)"
					fill={j > 5 ? 'var(--l-shape)' : 'var(--l-line)'}
				/>
			{/each}
		{:else if step === 'plus'}
			{#each plus as d, j (j)}<path {d} class="cell" />{/each}
		{:else if step === 'l'}
			{#each plus as d, j (j)}<path {d} class="ghost" />{/each}
			<path d="{rect(arm.top)}{rect(arm.centre)}{rect(arm.right)}" fill="var(--l-shape)" />
		{:else if step === 'open'}
			{#each plus as d, j (j)}<path {d} class="ghost" />{/each}
			{#each parts as d, j (j)}<path {d} fill="var(--l-shape)" />{/each}
			<path d={rect(arm.centre)} class="lifted" />
			<circle cx="120" cy={SPLIT} r="14" class="joint" />
		{:else if step === 'lean'}
			{#each parts as d, j (j)}<path {d} class="lifted" />{/each}
			<path d={LIGHTNING} class="strike" />
			<g transform={sheared}>{#each parts as d, j (j)}<path {d} class="cell-outline" />{/each}</g>
		{:else}
			<g transform={sheared}>{#each parts as d, j (j)}<path {d} class="ghost" />{/each}</g>
			{#each PATHS as d, j (j)}<path {d} fill="var(--l-shape)" />{/each}
			{#each corners as c, j (j)}<circle cx={c.centre[0]} cy={c.centre[1]} r={c.r} class="guide" />{/each}
		{/if}
	{/snippet}
</Figure>
