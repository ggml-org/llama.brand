<script lang="ts">
	let { glyphCount, size, tracking }: { glyphCount: number; size: number; tracking: number } = $props();
</script>

<section class="tester">
	<span class="label">Try it</span>
	<p
		class="text"
		contenteditable="true"
		spellcheck="false"
		aria-label="Editable sample text"
		style:font-size="{size}px"
		style:letter-spacing="{tracking / 1000}em"
	>
		Grotesk 42 / Quiet Monolines
	</p>
	<p class="hint">Click the text to edit it; size and tracking are in the bar above. All {glyphCount} glyphs are in, including accents and symbols.</p>
</section>

<style>
	.tester {
		display: grid;
		gap: 12px;
	}
	.text {
		margin: 0;
		padding: 20px;
		min-height: 1.4em;
		font-family: var(--display);
		font-weight: var(--w);
		line-height: 1.1;
		background: var(--sheet);
		border: 1px solid var(--rule);
		outline: none;
		overflow-wrap: anywhere;
	}
	.text:focus-visible {
		border-color: var(--guide);
		box-shadow: 0 0 0 3px var(--guide-soft);
	}
	.hint {
		margin: 0;
		font-size: 13px;
		color: var(--muted);
	}
</style>
