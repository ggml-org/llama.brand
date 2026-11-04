<!-- The version on show at work: Display's headlines, or UI's controls and then its running text. -->
<script lang="ts">
	import ShowcaseDisplay from './ShowcaseDisplay.svelte';
	import ShowcaseUI from './ShowcaseUI.svelte';
	import ShowcaseProse from './ShowcaseProse.svelte';

	let { variant, glyphCount, guides = false }: { variant: string; glyphCount: number; guides?: boolean } = $props();
</script>

<section class="in-use" aria-label="In use">
	{#if variant === 'Display'}
		<ShowcaseDisplay />
	{:else}
		<ShowcaseUI {glyphCount} {guides} />
		<ShowcaseProse />
	{/if}
</section>

<style>
	.in-use {
		display: grid;
		gap: 56px;
	}
</style>
