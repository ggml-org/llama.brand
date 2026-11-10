// The specimen's data, exported from the fonts by build_specimen.py (fonts come in via #lib/fonts/fonts.css).
import raw from './data/specimen.json';

export interface Cell {
	ch: string;
	adv: number;
	dx: number;
	d: string;
	prev?: string; // the earlier build's outline, when it differs
}

export interface Specimen {
	glyphCount: number;
	metrics: { upm: number; cap: number; x: number; asc: number; dsc: number };
	axis: { min: number; max: number };
	styles: { weight: number; name: string; stem: number }[];
	waterfall: { weight: number; name: string }[];
	variants: string[];
	compare: { labels: string[] } | null;
	/** the small-sizes section: its font sizes, and the units each advance gains there over opsz 16 */
	small: { sizes: number[]; tracking: number[]; prevTracking: number[] | null };
	grid: {
		variant: string;
		width: number;
		height: number;
		guides: { base: number; x: number; cap: number; asc: number; dsc: number };
		groups: { title: string; chars: string[] }[];
		cells: Record<string, Cell[]>;
	};
}

export const specimen = raw as unknown as Specimen;

/** each version's place on the optical size axis: Llama Sans is one font, and UI and Display are two of its named sizes (Small, at 10, has no version: text under 16 px takes it on its own) */
export const opsz: Record<string, number> = { Display: 36, UI: 16 };

export const fallback = '"Helvetica Neue", Arial, sans-serif';
