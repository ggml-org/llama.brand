<!-- One rule that shapes the icon, drawn over a faint icon: the two blades, the 60° edges, the shared diagonal,
     the split, the steps of 120 and the soft corners. The caption is the children. -->
<script lang="ts" module>
	export const RULES = ['blades', 'angle', 'diagonal', 'split', 'steps', 'corners'] as const;
	export type RuleName = (typeof RULES)[number];
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import Figure from './Figure.svelte';
	import { PATHS, SIZE, SPLIT, edges, corners } from '#lib/logo.ts';
	import { STEPS, lower } from '#lib/blueprint.ts';

	let { rule, title, children }: { rule: RuleName; title?: string; children?: Snippet } = $props();

	const titles: Record<RuleName, string> = {
		blades: 'Two blades',
		angle: '60° everywhere',
		diagonal: 'One diagonal',
		split: 'The split',
		steps: 'Steps of 120',
		corners: 'Soft outer corners'
	};
</script>

{#snippet icon(fill = 'var(--l-faint)')}
	{#each PATHS as d, i (i)}<path {d} {fill} />{/each}
{/snippet}

<Figure title={title ?? titles[rule]} {children}>
	{#snippet drawing()}
		{#if rule === 'blades'}
			<path d={PATHS[1]} fill="var(--l-shape)" />
			<path d={PATHS[0]} fill="var(--l-shape-2)" />
			<text x="150" y="250" class="note on-shape">upper blade</text>
			<text x="300" y="520" class="note on-shape">lower blade</text>
		{:else if rule === 'angle'}
			{@render icon()}
			{#each [[0, SPLIT], [240, SPLIT], [120, SIZE]] as [x, y], i (i)}
				<path d="M{x + 80} {y} A80 80 0 0 0 {x + 40} {y - 69.3}" class="arc" />
				<text x={x + 92} y={y - 26} class="note">60°</text>
			{/each}
			{#each [edges.upperLeft, edges.shared, edges.lowerRight] as [a, b], i (i)}
				<line x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} class="hi" />
			{/each}
		{:else if rule === 'diagonal'}
			{@render icon()}
			<line x1="466.154" y1="0" x2="120" y2="600" class="hi" />
			<circle cx="240" cy={SPLIT} r="12" class="joint" />
			<text x="270" y={SPLIT + 10} class="note">240, {SPLIT}</text>
		{:else if rule === 'split'}
			{@render icon()}
			<line x1="-40" y1={SPLIT} x2="640" y2={SPLIT} class="hi" />
			<line x1="-30" y1="0" x2="-30" y2={SPLIT} class="dim" />
			<line x1="-30" y1={SPLIT} x2="-30" y2={SIZE} class="dim" />
			<text x="-20" y={SPLIT / 2} class="note">{SPLIT}</text>
			<text x="-20" y={SPLIT + lower / 2 + 10} class="note">{lower}</text>
		{:else if rule === 'steps'}
			{@render icon()}
			{#each STEPS as x (x)}
				<line x1={x} y1="-40" x2={x} y2="616" class="hi" />
				<text {x} y="652" text-anchor="middle" class="note">{x}</text>
			{/each}
		{:else}
			{@render icon()}
			{#each corners as c, i (i)}
				<circle cx={c.centre[0]} cy={c.centre[1]} r={c.r} class="hi" />
				<line x1={c.sharp[0]} y1={c.sharp[1]} x2={c.tangentFlat[0]} y2={c.tangentFlat[1]} class="dim" />
				<circle cx={c.sharp[0]} cy={c.sharp[1]} r="8" class="joint" />
			{/each}
		{/if}
	{/snippet}
</Figure>
