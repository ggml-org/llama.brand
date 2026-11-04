<!--
	The template every +page.svx uses: the showcase's grey card around the Markdown and its components.
	Frontmatter: title (browser tab). In the Markdown, a <p class="kicker"> sits over an h2, and the paragraph right
	under the h2 is its lead.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, children }: { title: string; children: Snippet } = $props();
</script>

<svelte:head><title>{title}</title></svelte:head>

<main>
	<div class="logo">{@render children()}</div>
</main>

<style>
	main {
		max-width: 1180px;
		margin: 0 auto;
		padding-block: 16px 48px;
		padding-left: max(16px, env(safe-area-inset-left, 0px));
		padding-right: max(16px, env(safe-area-inset-right, 0px));
	}
	.logo {
		display: grid;
		gap: 40px;
		padding: clamp(16px, 4vw, 48px);
		border-radius: 16px;
		background: var(--l-bg);
		color: var(--l-ink);
	}
	.logo > :global(*) {
		margin: 0;
		min-width: 0;
	}
	/* a kicker, its heading, the lead and the sketch button read as one block, 10px apart */
	.logo > :global(.kicker) {
		margin-bottom: -30px;
		font: 500 12px var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--l-muted);
	}
	.logo > :global(h2) {
		font: 700 clamp(32px, 5vw, 56px) / normal 'Llama Sans Display', var(--body);
	}
	.logo > :global(h2 + p) {
		max-width: 62ch;
		margin-top: -30px;
		color: var(--l-muted);
		font: 400 17px / normal 'Llama Sans Text', var(--body);
	}
	.logo > :global(h2 + p + .sketch-open) {
		margin-top: -30px;
	}
	/* the origin's tiles sit closer under their heading */
	.logo > :global(.steps) {
		margin-top: -20px;
	}
</style>
