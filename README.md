# Politics Through Time

An interactive star-chart timeline of **45 political systems and ideologies**, from tribal councils and the first kings to neoliberalism, populism and national conservatism.

**Live page:** https://petrogko.github.io/politics-history-timeline/

![Politics Through Time](docs/preview.png)

## How to read it

- **The band across the middle is time.** By default recent centuries are stretched, because almost every modern ideology is less than 250 years old; switch to **True to time** to see every century at the same width.
- **Above the line:** set out by a founding thinker or leader (Locke, Burke, Marx, Keynes…).
- **Below the line:** grew out of movements, events or custom (parliament, nationalism, populism…).
- **Star size:** influence today (worldwide · major · significant · minor). A hollow star means the system is no longer practised. Influence is a judgment, not a measurement.
- **Lines:** *grew out of* (solid), *drew on* (dashed) and *reacted against* (dotted).
- **Tap a star** for how it began, its core ideas, key texts, its main criticism, where it stands today, and what came before and after it. Family chips filter the chart; **List** shows everything as a table. Each entry has its own link (e.g. `#marxism`).

The nine families: Democracy & republics, Liberal, Conservative & traditional, Socialist & left, Rule by one or few, Nation & people, Faith & politics, Economic ideas, and Reform & rights movements.

## Neutrality

Each entry describes an idea in its own terms and gives its main criticism; inclusion is not endorsement. The palette deliberately avoids red and blue so no family reads as partisan. Dates are approximate: most ideas grew over decades, and each star sits at a widely used starting point (a founding text, a first party, a first government).

## Editing

All content lives in one file, `src/politics-through-time.html`, in the `D` array near the top of the script. Each entry looks like:

```js
{ id: "marxism", label: "Marxism", name: "Marxism", fam: "left", y: 1848, ds: "1848",
  date: "1848 (The Communist Manifesto)", how: "founded", size: "l", status: "Living",
  story: "…", ideas: "…", texts: "…", critique: "…", today: "…",
  parents: [["utopian", "drew"], ["laissezfaire", "against"]], wiki: "Marxism" }
```

- `y` is the plotted year (negative = BCE); undated entries use `pre` (a slot in the block on the left) instead.
- Optional: `range: [start, end]` + `rangeLabel` for a gradual or debated start; `end` + `endLabel` for systems that ended.
- `how`: `founded` (above the line) or `grew` (below). `size`: `xl`, `l`, `m`, `s`, or `none` (no longer practised).
- `parents`: `[id, kind]` pairs, where kind is `grew`, `drew` or `against`.

Then rebuild the GitHub Pages file:

```sh
python3 build.py
```

`build.py` wraps the source in a full HTML page as `index.html` and refuses to write it if the data has a problem (duplicate ids, a relationship to an entry that doesn't exist, or a line running backwards in time). The source file itself is the version published as a Claude artifact, which adds its own page skeleton.

## Credits

Summaries written for this chart from standard histories, with Wikipedia links for further reading. Companion to *Religions Through Time*. Fonts: Libre Caslon (the Caslon face set the 1776 Declaration broadside) and IBM Plex.
