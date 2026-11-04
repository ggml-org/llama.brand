<script lang="ts">
	import { specimen } from '#lib/specimen.ts';

	let {
		weight = $bindable(),
		variant = $bindable(),
		size = $bindable(),
		tracking = $bindable(),
		guides = $bindable()
	}: {
		weight: number;
		variant: string;
		size: number;
		tracking: number;
		guides: boolean;
	} = $props();

	const { styles, variants, axis } = specimen;
	// the named weight closest to the slider; the glyph grid is drawn at named weights only
	const named = $derived(
		styles.reduce((a, s) => (Math.abs(s.weight - weight) < Math.abs(a.weight - weight) ? s : a)).weight
	);
</script>

<div class="bar">
	<span class="label">Weight</span>
	<div class="segmented" role="radiogroup" aria-label="Weight">
		{#each styles as s (s.weight)}
			<label>
				<input type="radio" name="weight" checked={named === s.weight} onchange={() => (weight = s.weight)} />
				<span>{s.name} <em>{s.weight}</em></span>
			</label>
		{/each}
	</div>

	<div class="group">
		<span class="label">Version</span>
		<div class="segmented" role="radiogroup" aria-label="Version">
			{#each variants as v (v)}
				<label>
					<input type="radio" name="variant" value={v} bind:group={variant} />
					<span>{v}</span>
				</label>
			{/each}
		</div>
		<span class="kbd">press V</span>
	</div>


	<label class="slider" for="wght">
		Fine <input id="wght" type="range" min={axis.min} max={axis.max} step="1" bind:value={weight} />
		<output>{weight}</output>
	</label>

	<div class="row">
		<span class="label">Try it</span>
		<label class="slider">
			Size <input type="range" min="16" max="160" bind:value={size} /> <output>{size}</output>
		</label>
		<label class="slider">
			Tracking <input type="range" min="-40" max="120" bind:value={tracking} /> <output>{tracking}</output>
		</label>
		<label class="toggle"><input type="checkbox" bind:checked={guides} /> Show line boxes</label>
	</div>
</div>

<style>
	.bar {
		position: sticky;
		top: env(safe-area-inset-top, 0px);
		z-index: 5;
		display: flex;
		flex-wrap: wrap;
		gap: 8px 16px;
		align-items: center;
		padding-block: 10px;
		background: var(--paper);
		border-bottom: 1px solid var(--rule);
	}
	/* on phones every control together is a third of the screen: let it scroll away instead */
	@media (max-width: 600px) {
		.bar {
			position: static;
		}
	}
	.group {
		display: flex;
		gap: 8px;
		align-items: center;
	}
	.group:first-of-type {
		margin-left: auto;
	}
	.kbd {
		font: 400 11px var(--mono);
		color: var(--muted);
	}
	.slider {
		display: flex;
		gap: 10px;
		align-items: center;
		font: 400 12px var(--mono);
		color: var(--muted);
	}
	.slider input {
		accent-color: var(--ink);
		width: 180px;
	}
	.slider output {
		min-width: 3ch;
		font-variant-numeric: tabular-nums;
	}
	.row {
		flex-basis: 100%;
		display: flex;
		flex-wrap: wrap;
		gap: 8px 20px;
		align-items: center;
		padding-top: 8px;
		border-top: 1px dashed var(--rule);
	}
	.row .slider input {
		width: 150px;
		accent-color: var(--guide);
	}
	.toggle {
		display: flex;
		gap: 8px;
		align-items: center;
		font: 400 12px var(--mono);
		color: var(--muted);
		cursor: pointer;
	}
	.toggle input {
		accent-color: var(--guide);
	}
</style>
