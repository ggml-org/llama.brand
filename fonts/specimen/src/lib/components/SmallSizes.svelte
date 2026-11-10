<!--
	Text at the small sizes, each line at the optical size of its font-size (not the page's pinned one), with the
	tracking the font adds there. Adjust tries more or less of it before it goes into the font: the units added at
	10 px, easing to none at 16 px, the way the axis itself runs.
-->
<script lang="ts">
	import { specimen } from '#lib/specimen.ts';

	let { comparing = false }: { comparing?: boolean } = $props();

	const { sizes, tracking, prevTracking } = specimen.small;
	const [smallest, largest] = [sizes[0], sizes[sizes.length - 1]];
	const built = $derived(comparing && prevTracking ? prevTracking : tracking);
	let adjust = $state(0);
	const extra = (size: number) => (adjust * (largest - size)) / (largest - smallest);
	const signed = (n: number) => (n > 0 ? '+' : n < 0 ? '−' : '') + Math.abs(Math.round(n));
</script>

<section class="small" aria-label="Small sizes">
	<label class="slider">
		Adjust <input type="range" min="-30" max="30" step="1" bind:value={adjust} />
		<output>{signed(adjust)} at {smallest} px</output>
	</label>
	{#each sizes as size, i (size)}
		<div class="srow">
			<span class="label">{size} px · {signed(built[i] + extra(size))}</span>
			<div class="sample" style:font-size="{size}px" style:letter-spacing="{extra(size) / 1000}em">
				<p class="ui">Download model · 4.7 GB · Q4_K_M · needs at least 16 GB memory</p>
				<p>
					A local model answers from your own machine: nothing leaves it, and it keeps working offline. Pick a
					quantisation that fits in memory, then raise the context length until replies slow down.
				</p>
			</div>
		</div>
	{/each}
</section>

<style>
	.small {
		--opsz-pin: normal; /* each line keeps the optical size of its font-size */
		display: grid;
		gap: 18px;
	}
	.srow {
		display: grid;
		grid-template-columns: 9ch 1fr;
		gap: 4px 20px;
		align-items: baseline;
	}
	.sample {
		display: grid;
		gap: 0.35em;
		max-width: 62ch;
		font-family: var(--display);
		font-weight: var(--w);
		line-height: 1.45;
	}
	.sample p {
		margin: 0;
	}
	.ui {
		font-weight: 500;
	}
	.slider {
		display: flex;
		gap: 10px;
		align-items: center;
		font: 400 12px var(--mono);
		color: var(--muted);
	}
	.slider input {
		width: 180px;
		accent-color: var(--guide);
	}
	.slider output {
		font-variant-numeric: tabular-nums;
	}
	@media (max-width: 600px) {
		.srow {
			grid-template-columns: 1fr;
		}
	}
</style>
