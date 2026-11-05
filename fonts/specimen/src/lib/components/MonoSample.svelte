<!-- Llama Mono at one weight: a few lines of code, set in its 600-unit cells. -->
<script lang="ts">
	let {
		weight,
		code = `fn attest(state: &State) -> Result<u32> {
    let total = 0x1F40 + 12_345; // settle
    if total >= limit && !state.pretty { return Err(e); }
    Ok(total) // ilI1| O0 {} [] =>  Llama
}`
	}: { weight: number; code?: string } = $props();
</script>

<pre class="mono" aria-label="Llama Mono sample" style:font-weight={weight}>{code}</pre>

<style>
	.mono {
		margin: 0;
		padding: 20px 24px;
		background: var(--sheet);
		border-radius: 12px;
		font-family: var(--code);
		font-size: clamp(13px, 1.8vw, 20px);
		line-height: 1.6;
		overflow-x: auto;
	}
</style>
