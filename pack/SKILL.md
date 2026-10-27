---
name: wardrobe-scout
description: Shows a person what they would look like in new outfits before they buy, using their own photo, then finds those pieces second-hand and puts them on one shopping list page for their phone. Generates rounds of four full-body looks through an image API the person already has a key for (OpenAI, Gemini or fal), can start from pins of a style they like and change a single piece of a look, searches Vinted, Depop, Vestiaire Collective and eBay in their own signed-in browser, checks fabric, size, measurements and shipping on each listing, skips fast-fashion copies, drafts questions for sellers in the listing's language, and rechecks the list later for sold listings. Use when someone says "help me find a new style", "show me outfits on me", "I like this style on Pinterest", "change only the shoes in that look", "find these on Vinted", "what would this cost used", "make me a page with the links", or the same in Portuguese ("me ajuda a mudar meu estilo", "gera looks com a minha foto", "troca só o tênis", "procura no Vinted", "monta uma página com os links") or any other language. Never buys anything.
license: MIT
---

# Wardrobe Scout

Three jobs, one file each. Look at what the person asks and at their working folder (`wardrobe/`, with `profile.md`, `looks/` and `finds.json` once they exist), and pick:

- **Looks** (no looks yet, a new round, pins of a style they like, or "change only the shoes in that look"): follow [references/looks.md](references/looks.md).
- **The hunt** (find the pieces of the liked looks in second-hand shops, or recheck an existing list for sold listings): follow [references/hunt.md](references/hunt.md).
- **The list** (turn `finds.json` into the page for their phone, or rebuild it after a recheck): follow [references/list.md](references/list.md).

The usual order is looks, then hunt, then list, and each file says when to hand over to the next. Each file opens with its non-negotiable rules: read them before touching any of the person's files or opening a shop.

## `SKILL_DIR`

In the commands of the three files, `${SKILL_DIR}` is the folder this `SKILL.md` is in. Replace it with that folder's real path before running a command.

## Next to this file

- `scripts/generate_look.py`: one look from 1 to 4 photos of the person, or an edit of a liked look with `--edit`. Providers `openai`, `gemini` and `fal`; GPT Image 2.5 is the default with an OpenAI key and with a fal key. Python standard library only.
- `scripts/build_list.py`: `finds.json` to a single HTML page, with English and Portuguese labels built in. Python standard library only.
- `templates/`: `profile.md` (the person's answers, sizes and rules) and `shopping-list.css` (read by `build_list.py`).
- `examples/`: a fictional `finds.json` for Lucas, a synthetic person, with three of his looks in `examples/images/`. That is the bar for the page.
- `references/stores.md`: search addresses, fees and quirks per shop, and search words in several languages.
- `DISCLAIMER.md` and `LICENSE` (MIT).

## What the person needs

- **Python 3.9 or newer.** The scripts use only the standard library and install nothing.
- **An image API key from one provider**, set as an environment variable: `OPENAI_API_KEY`, `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) or `FAL_KEY`. Each image is billed by that provider to the person's own account.
- **A browser the agent can use**, where the person signs in to the shops themself.
