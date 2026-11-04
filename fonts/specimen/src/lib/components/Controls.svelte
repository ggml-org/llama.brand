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
	// on phones the bar floats at the bottom with weight and version only; the rest opens on request
	let more = $state(false);
</script>

<div class="bar" class:more>
	<span class="label">Weight</span>
	<div class="segmented weights" role="radiogroup" aria-label="Weight">
		{#each styles as s (s.weight)}
			<label>
				<input type="radio" name="weight" checked={named === s.weight} onchange={() => (weight = s.weight)} />
				<span>{s.name} <em>{s.weight}</em></span>
			</label>
		{/each}
	</div>

	<div class="group versions">
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
		<button type="button" class="more-toggle" aria-expanded={more} aria-controls="more-controls" onclick={() => (more = !more)}>
			{more ? 'Less' : 'More'}
		</button>
	</div>

	<div class="extra" id="more-controls">
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
	/* the fine slider and the Try it row sit in the bar's own flow on wide screens */
	.extra {
		display: contents;
	}
	.more-toggle {
		display: none;
	}
	/* on phones the bar floats at the bottom of the screen: weight and version always, the rest behind More */
	@media (max-width: 600px) {
		.bar {
			position: fixed;
			top: auto;
			left: max(8px, env(safe-area-inset-left, 0px));
			right: max(8px, env(safe-area-inset-right, 0px));
			bottom: calc(8px + env(safe-area-inset-bottom, 0px));
			z-index: 20;
			flex-direction: column;
			align-items: stretch;
			gap: 8px;
			max-height: min(70vh, 520px);
			overflow-y: auto;
			padding: 8px;
			border: 1px solid var(--rule);
			border-radius: 14px;
			box-shadow: 0 8px 28px rgba(0, 0, 0, 0.22);
		}
		.bar > .label,
		.versions .label,
		.kbd {
			display: none;
		}
		.segmented label {
			flex: 1;
		}
		.segmented label span {
			text-align: center;
			padding: 8px 6px;
		}
		.versions {
			margin-left: 0;
		}
		.versions .segmented {
			flex: 1;
		}
		.more-toggle {
			display: block;
			padding: 8px 12px;
			border: 1px solid var(--rule);
			border-radius: 8px;
			background: none;
			color: var(--ink);
			font: 500 13px var(--mono);
			cursor: pointer;
		}
		.more-toggle:focus-visible {
			outline: 2px solid var(--guide);
			outline-offset: 2px;
		}
		.extra {
			display: none;
		}
		.more .extra {
			display: grid;
			gap: 10px;
			order: -1; /* opens above the switches, toward the page */
			padding: 4px 4px 10px;
			border-bottom: 1px dashed var(--rule);
		}
		.slider input,
		.row .slider input {
			flex: 1;
			width: auto;
			min-width: 0;
		}
		.row {
			display: grid;
			gap: 10px;
			padding-top: 0;
			border-top: 0;
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
