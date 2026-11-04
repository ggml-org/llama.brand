<!-- The version on show at work: the Display, UI or Text showcase. -->
<script lang="ts">
	import ShowcaseDisplay from './ShowcaseDisplay.svelte';
	import ShowcaseUI from './ShowcaseUI.svelte';
	import ShowcaseText from './ShowcaseText.svelte';

	let { variant, glyphCount, guides = false }: { variant: string; glyphCount: number; guides?: boolean } = $props();
</script>

<section aria-label="In use">
	{#if variant === 'Display'}
		<ShowcaseDisplay />
	{:else if variant === 'UI'}
		<ShowcaseUI {glyphCount} {guides} />
	{:else}
		<ShowcaseText />
	{/if}
</section>
