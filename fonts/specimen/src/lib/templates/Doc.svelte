<!--
	The template every +page.svx uses: the page frame, set in the version (an optical size, pinned with opsz) and
	weight the page is showing, with the
	keyboard shortcuts (V for the next version, B to compare builds). Frontmatter: title (browser tab).
	Markdown h2s are the section labels; the paragraph right under one is its quiet note.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { specimen, fallback, opsz } from '#lib/specimen.ts';
	import { view } from '#lib/view.svelte.ts';

	let { title, children }: { title: string; children: Snippet } = $props();

	// comparing swaps the font for the earlier build's, at the same optical size
	const family = $derived(`"Llama Sans${view.comparing ? ' Prev' : ''}", ${fallback}`);

	function onkeydown(e: KeyboardEvent) {
		const t = e.target as HTMLElement;
		if (e.metaKey || e.ctrlKey || e.altKey) return;
		const typing = t.isContentEditable || (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) &&
			!['radio', 'range', 'checkbox'].includes((t as HTMLInputElement).type));
		if (typing) return;
		const key = e.key.toLowerCase();
		const { variants } = specimen;
		if (key === 'v') view.variant = variants[(variants.indexOf(view.variant) + 1) % variants.length];
		if (key === 'b' && specimen.compare) view.comparing = !view.comparing;
	}
</script>

<svelte:head><title>{title}</title></svelte:head>
<svelte:window {onkeydown} />

<div class="wrap" style:--w={view.weight} style:--display={family}
	style:--opsz-pin={`'opsz' ${opsz[view.variant] ?? 16}`}>{@render children()}</div>

<style>
	.wrap {
		max-width: 1180px;
		margin: 0 auto;
		padding-block: 40px 80px;
		padding-left: max(16px, env(safe-area-inset-left, 0px));
		padding-right: max(16px, env(safe-area-inset-right, 0px));
		display: grid;
		gap: 56px;
	}
	.wrap > :global(*) {
		margin: 0;
		min-width: 0;
	}
	/* a section label sits 12px above its section, and its note just under it */
	.wrap > :global(h2) {
		margin-bottom: -44px;
		font: 500 11px/1.4 var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.wrap > :global(h2 + p) {
		--opsz-pin: normal; /* the page's own notes keep the optical size of their font-size */
		margin-bottom: -38px;
		font-size: 13px;
		color: var(--muted);
	}
	/* the design notes close on the next pass and the licence */
	.wrap > :global(.notes + p) {
		max-width: 70ch;
		margin-top: -42px;
		color: var(--muted);
	}
	/* room at the bottom on phones, where the controls float over the page; there the notes step aside */
	@media (max-width: 600px) {
		.wrap {
			padding-bottom: calc(150px + env(safe-area-inset-bottom, 0px));
		}
		.wrap > :global(:is(h2 + p, h2:has(+ .notes), .notes + p)) {
			display: none;
		}
	}
</style>
