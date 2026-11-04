<script lang="ts">
	import LogoPage from '#lib/components/LogoPage.svelte';
</script>

<main>
	<LogoPage />
</main>

<style>
	main {
		max-width: 1180px;
		margin: 0 auto;
		padding-block: 16px 48px;
		padding-left: max(16px, env(safe-area-inset-left, 0px));
		padding-right: max(16px, env(safe-area-inset-right, 0px));
	}
</style>
