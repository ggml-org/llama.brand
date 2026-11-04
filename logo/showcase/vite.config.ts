import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
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
