import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { mdsvex } from 'mdsvex';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		mdsvex({
			extensions: ['.svx'],
			// pages (+page.svx) get the Doc template: the page frame around the Markdown and its components
			templates: { default: '#lib/templates/Doc.svelte' },
			select_template: (id) => (id.includes('/src/routes/') ? undefined : false)
		}),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			// A prerendered static site...
			adapter: adapter(),
			// ...built into one self-contained build/index.html: scripts and styles inlined
			output: { bundleStrategy: 'inline' }
		})
	],
	build: {
		// inline imported assets (the fonts) too, so index.html works on its own
		assetsInlineLimit: 50_000_000
	}
});
