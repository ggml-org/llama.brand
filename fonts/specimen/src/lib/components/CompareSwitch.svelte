<!-- Floating Before / After switch for the whole page, shown when the specimen was exported with --prev-fonts. -->
<script lang="ts">
	let { comparing = $bindable(), labels }: { comparing: boolean; labels: string[] } = $props();
</script>

<div class="compare" role="radiogroup" aria-label="Compare builds">
	<div class="segmented">
		<label>
			<input type="radio" name="compare" checked={comparing} onchange={() => (comparing = true)} />
			<span>{labels[0]}</span>
		</label>
		<label>
			<input type="radio" name="compare" checked={!comparing} onchange={() => (comparing = false)} />
			<span>{labels.at(-1)}</span>
		</label>
	</div>
	<span class="kbd">B</span>
</div>

<style>
	.compare {
		position: fixed;
		z-index: 20;
		left: 50%;
		bottom: calc(16px + env(safe-area-inset-bottom, 0px));
		transform: translateX(-50%);
		display: flex;
		gap: 10px;
		align-items: center;
		padding: 6px 8px 6px 6px;
		border: 1px solid var(--rule);
		border-radius: 10px;
		background: var(--paper);
		box-shadow: 0 6px 24px rgba(0, 0, 0, 0.18);
	}
	.segmented {
		border-radius: 7px;
	}
	.kbd {
		padding: 2px 7px;
		border: 1px solid var(--rule);
		border-radius: 5px;
		font: 500 11px var(--mono);
		color: var(--muted);
	}
</style>
