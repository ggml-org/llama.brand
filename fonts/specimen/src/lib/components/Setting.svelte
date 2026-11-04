<!-- A sample setting at one weight: a headline over a line of body. -->
<script lang="ts">
	let {
		weight,
		headline = 'Hamburgefonstiv 2026',
		line = 'Sphinx of black quartz, judge my vow. 0123456789'
	}: { weight: number; headline?: string; line?: string } = $props();
</script>

<section class="setting" aria-label="Sample setting" style:font-weight={weight}>
	<p class="s1">{headline}</p>
	<p class="s2">{line}</p>
</section>

<style>
	.setting {
		display: grid;
		gap: 12px;
	}
	p {
		margin: 0;
		font-family: var(--display);
		overflow-wrap: anywhere;
	}
	.s1 {
		font-size: clamp(34px, 6vw, 76px);
		line-height: 1.02;
	}
	.s2 {
		font-size: clamp(20px, 3vw, 34px);
		line-height: 1.2;
		color: var(--muted);
	}
</style>
