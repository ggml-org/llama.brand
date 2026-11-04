<script lang="ts">
	import { specimen } from '#lib/specimen.ts';

	const stems = specimen.styles.map((s) => s.stem);
	const notes: [string, string][] = [
		['Stroke', `Near-monoline, with a ${stems[0]}-unit stem at 400 rising to ${stems.at(-1)} at 700. Joins stay clean, without ink traps.`],
		['Curves', 'Bowls are eased toward true circles, fully circular in G, S and s, so rounds read soft and calm without turning geometric.'],
		['Terminals', 'Every curved stroke end is trimmed the same short distance and cut almost square to the stroke, which keeps c, e, g, s, 2, 3, 5, 6 and 9 open and consistent.'],
		['a', 'Double-story, on a straight stem with a flat foot. The hook runs long and ends in a flat cut; the bowl rises gently into the stem with sharp joints. Toward Bold, a small bracketed foot appears.'],
		['l, r, t, f', 'A plain l the width of the i. The ends of r, t and f are angled to match the curved terminals.'],
		['G, S, s', 'Wide and round, with slightly open, angled ends on S and s.'],
		['Display', 'For headlines and large sizes: tracking −26, stronger kerning (115%) and compact 1.15 em line spacing.'],
		['UI', 'For buttons, cards and labels: tracking −4, kerning like Display’s but a little wider, and a 1.25 em line box centred on the cap height.'],
		['Text', 'For long prose at small sizes: tracking +10, softer kerning (85%, with gentle pair corrections) and 1.5 em line spacing built into the font.'],
	];
</script>

<section class="notes">
	<span class="label">Design notes</span>
	<dl>
		{#each notes as [term, text] (term)}
			<div><dt>{term}</dt><dd>{text}</dd></div>
		{/each}
	</dl>
	<p class="next">
		Next pass: a straight-legged R and a shorter Q tail, an angled end on the j, slightly wider o, c, e and O, and a
		review of the accented glyphs. Licence: SIL Open Font License 1.1. Llama Sans is derived from Geist, © 2024 The
		Geist Project Authors.
	</p>
</section>

<style>
	.notes {
		display: grid;
		gap: 14px;
	}
	dl {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
		gap: 18px 28px;
		margin: 0;
	}
	dl div {
		display: grid;
		gap: 4px;
		min-width: 0;
		padding-top: 10px;
		border-top: 1px solid var(--rule);
	}
	dt {
		font: 500 11px var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--muted);
	}
	dd {
		margin: 0;
		font-size: 15px;
		line-height: 1.5;
	}
	.next {
		max-width: 70ch;
		margin: 0;
		color: var(--muted);
	}
</style>
