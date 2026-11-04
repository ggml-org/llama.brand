<!-- The original pencil sketch (src/lib/assets/sketch.webp), behind a button; without the file nothing renders. -->
<script lang="ts">
	let { label = 'View the original sketch' }: { label?: string } = $props();

	const sketches = import.meta.glob('../assets/sketch.{jpg,jpeg,png,webp,avif}', {
		eager: true,
		query: '?url',
		import: 'default'
	}) as Record<string, string>;
	const sketch = Object.values(sketches)[0];
	let dialog = $state<HTMLDialogElement>();
</script>

{#if sketch}
	<button type="button" class="sketch-open" onclick={() => dialog?.showModal()}>{label}</button>
	<dialog class="sketch" bind:this={dialog} closedby="any" aria-label="The original pencil sketch">
		<img src={sketch} alt="A sketchbook page in pencil: a slanted plus, the same plus with its top and right arms shaded, the two-blade icon in a rounded square, an upright plus with two arms shaded, L shapes built on a grid and an L drawn in perspective" />
		<form method="dialog"><button class="sketch-close">Close</button></form>
	</dialog>
{/if}

<style>
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
</style>
