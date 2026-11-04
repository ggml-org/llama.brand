<!-- One step of where the icon comes from, as a tile: the plus, the L inside it, the opened corner, the bolt, the
     lean and the softened corners. The caption is the children. -->
<script lang="ts" module>
	export const ORIGIN_STEPS = ['plus', 'l', 'open', 'bolt', 'lean', 'soften'] as const;
	export type OriginStepName = (typeof ORIGIN_STEPS)[number];
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import Figure from './Figure.svelte';
	import { PATHS, SPLIT, corners } from '#lib/logo.ts';
	import { LIGHTNING } from '#lib/origin.ts';
	import { arm, plus, parts, rect, sheared } from '#lib/blueprint.ts';

	let { step, title, children }: { step: OriginStepName; title?: string; children?: Snippet } = $props();

	const titles: Record<OriginStepName, string> = {
		plus: 'Plus',
		l: 'L',
		open: 'Open the corner',
		bolt: 'Bolt',
		lean: 'Lean',
		soften: 'Soften'
	};
	// one scale for every tile: the upright frames fit the whole plus, the leaning ones centre the icon
	const upright = '-560 -64 1120 1120';
	const leaning = '-260 -260 1120 1120';
	const i = $derived(ORIGIN_STEPS.indexOf(step));
</script>

<Figure n={String(i + 1).padStart(2, '0')} title={title ?? titles[step]} view={i < 3 ? upright : leaning} {children}>
	{#snippet drawing()}
		{#if step === 'plus'}
			{#each plus as d, j (j)}<path {d} class="cell" />{/each}
		{:else if step === 'l'}
			{#each plus as d, j (j)}<path {d} class="ghost" />{/each}
			<path d="{rect(arm.top)}{rect(arm.centre)}{rect(arm.right)}" fill="var(--l-shape)" />
		{:else if step === 'open'}
			{#each plus as d, j (j)}<path {d} class="ghost" />{/each}
			{#each parts as d, j (j)}<path {d} fill="var(--l-shape)" />{/each}
			<path d={rect(arm.centre)} class="lifted" />
			<circle cx="120" cy={SPLIT} r="14" class="joint" />
		{:else if step === 'bolt'}
			<path d={LIGHTNING} class="strike" />
			{#each parts as d, j (j)}<path {d} class="cell-outline" />{/each}
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
