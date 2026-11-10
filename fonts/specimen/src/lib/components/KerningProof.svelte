<!--
	Headlines and short sentences made of the pairs that go wrong first: diagonals against rounds and stems (AV, To,
	Wa, Ty), open letters before punctuation (F., P., r, y.), quotes, f and its neighbours, and figures around 1 and 7.
	Each line sets at the optical size of its font-size, so the three groups show Display, UI and Small. The text is
	editable, and Kerning off sets the same line by advances alone.
-->
<script lang="ts">
	const groups = [
		{
			label: 'Headlines · 56 px',
			size: 56,
			lines: [
				'Today We Type Away',
				'Vowel Years, Wavy Tones',
				'LATVIA TAKES A YAWL TO TOKYO',
				'P. F. Kafka, Port Avery, Box 1741',
				'“Affair” or ‘fjord’? Try every key.',
				'Kafka’s quartz Sphinx, TV at 7:47'
			]
		},
		{
			label: 'Sentences · 16 px',
			size: 16,
			lines: [
				'We’re away. You’ll type “Yes” to Tokyo, Vera says, by Tuesday.',
				'Fry two very wavy kiwi (or try rye), next to L’Avenue, at 7 a.m.',
				'T. A. Yates, P. J. Avery & F. W. Taylor, Jr. wrote “LAYOUT” for AT&T.',
				'After every effort, a raffle: off by five, fjord, waffle, shelf life.',
				'Rather wavy toys vex royalty; try my xylophone, key by key.',
				'11/17/1974 at 7:41, 74.1% of $1,117.00, 0.71 × 47 = 33.37',
				'AWAY TOYOTA LYRIC AVOW KAYAK WATT PAYOUT RAFT FATAL TWELFTH'
			]
		},
		{
			label: 'Small · 12 px',
			size: 12,
			lines: [
				'We’re away. You’ll type “Yes” to Tokyo, Vera says, by Tuesday.',
				'T. A. Yates, P. J. Avery & F. W. Taylor, Jr. wrote “LAYOUT” for AT&T.',
				'Rather wavy toys vex royalty; try my xylophone, key by key.',
				'11/17/1974 at 7:41, 74.1% of $1,117.00, 0.71 × 47 = 33.37'
			]
		}
	];
	let off = $state(false);
</script>

<section class="kerning" class:off aria-label="Kerning proof">
	<label class="toggle"><input type="checkbox" bind:checked={off} /> Kerning off</label>
	{#each groups as g (g.label)}
		<div class="group">
			<span class="label">{g.label}</span>
			{#each g.lines as line (line)}
				<p contenteditable="true" spellcheck="false" style:font-size="{g.size}px">{line}</p>
			{/each}
		</div>
	{/each}
</section>

<style>
	.kerning {
		--opsz-pin: normal; /* each line keeps the optical size of its font-size */
		display: grid;
		gap: 28px;
	}
	.kerning.off p {
		font-kerning: none;
	}
	.group {
		display: grid;
		gap: 6px;
	}
	p {
		margin: 0;
		font-family: var(--display);
		font-weight: var(--w);
		line-height: 1.2;
		overflow-wrap: anywhere;
		outline: none;
	}
	.toggle {
		display: flex;
		gap: 8px;
		align-items: center;
		font: 400 12px var(--mono);
		color: var(--muted);
		cursor: pointer;
	}
</style>
