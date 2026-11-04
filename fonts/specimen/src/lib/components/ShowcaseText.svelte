<!-- Llama Sans Text in its element: reading. Body copy uses the font's own 1.5 em line spacing. -->
<script lang="ts">
	import TextGallery from './TextGallery.svelte';
</script>

<div class="text-showcase">
<article class="article">
	<header class="article-head">
		<p class="kicker">Notes on type · 4 min read</p>
		<h2 class="title">Why a text face needs room to breathe</h2>
		<p class="standfirst">
			Spacing that looks right in a headline feels cramped in a paragraph. Llama Sans Text opens up the letters and the
			lines so long reading stays easy.
		</p>
	</header>

	<div class="body">
		<p>
			At reading sizes the eye moves along a line in small jumps, taking in a few letters at a time. If those letters sit
			too close, words start to blur into each other; too far apart, and they stop reading as words at all. Text sits
			ten units looser than the drawn spacing and softens the kerning to 85%, so pairs like “To” and “AV” stay tidy
			without pinching.
		</p>
		<p>
			Line spacing does the rest. Text carries 1.5 em of leading inside the font itself, which means a paragraph set
			with <code>line-height: normal</code> already has comfortable gaps between its lines. Long passages keep an even
			grey texture instead of dark bands.
		</p>
		<blockquote>
			<p>Good text type disappears. You notice the words, not the letters.</p>
		</blockquote>
		<p>A few things the Text version is tuned for:</p>
		<ul>
			<li>Articles, documentation and long-form writing on screens.</li>
			<li>Small sizes, from captions at 13 px to body copy at 16–20 px.</li>
			<li>Mixed figures and letters, like 4 November 2026 or 974 glyphs.</li>
		</ul>
		<figure class="figure">
			<div class="figure-art" aria-hidden="true">Aa</div>
			<figcaption>Figure 1. The same outlines as Display and UI, spaced for reading.</figcaption>
		</figure>
		<p class="footnote">
			¹ Text, UI and Display share every outline; only spacing, kerning and line spacing change between them.
		</p>
	</div>
</article>

<TextGallery />
</div>

<style>
	.text-showcase {
		display: grid;
		gap: 40px;
	}
	.article {
		display: grid;
		gap: 28px;
		max-width: 68ch;
		font-family: var(--display);
	}
	p,
	h2,
	blockquote,
	ul,
	figure {
		margin: 0;
	}
	.article-head {
		display: grid;
		gap: 10px;
	}
	.kicker {
		font: 500 13px / normal var(--display);
		color: var(--muted);
		letter-spacing: 0.02em;
	}
	.title {
		font: 600 clamp(28px, 4vw, 40px) / normal var(--display);
		text-wrap: balance;
	}
	.standfirst {
		font: 400 clamp(18px, 2.2vw, 21px) / normal var(--display);
		color: var(--muted);
	}
	.body {
		display: grid;
		gap: 1em;
		font: var(--w) 17px / normal var(--display);
	}
	code {
		font: 400 0.88em var(--mono);
		padding: 0.05em 0.35em;
		border-radius: 4px;
		background: var(--sheet);
		border: 1px solid var(--rule);
	}
	blockquote {
		padding: 4px 0 4px 18px;
		border-left: 3px solid var(--guide);
	}
	blockquote p {
		font: 500 20px / normal var(--display); /* no italic yet: never let the browser fake one */
	}
	ul {
		display: grid;
		gap: 0.35em;
		padding-left: 1.2em;
	}
	.figure {
		display: grid;
		gap: 8px;
	}
	.figure-art {
		display: grid;
		place-items: center;
		aspect-ratio: 16 / 6;
		max-width: 100%;
		border-radius: 10px;
		background: var(--sheet);
		border: 1px solid var(--rule);
		font: var(--w) clamp(64px, 12vw, 140px) / 1 var(--display);
	}
	figcaption {
		font: 400 13px / normal var(--display);
		color: var(--muted);
	}
	.footnote {
		font: 400 13px / normal var(--display);
		color: var(--muted);
	}
</style>
