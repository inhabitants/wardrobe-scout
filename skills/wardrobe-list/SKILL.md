---
name: wardrobe-list
description: Turns the listings found by wardrobe-hunt (finds.json) into one shopping list page the person can open on their phone while they buy - one section per piece with the look it belongs to, three ranked listings with fit labels, total price with shipping, an index, "bought" boxes, a look picker that lights up only the pieces of the look the person taps and says what is left to buy, a copy button with a ready message for the seller, and sold listings moved out on their own. Use after wardrobe-hunt, or when someone says "make me a page with the links", "put the shopping list somewhere I can open on my phone", "let me pick a look and see its pieces", or the same in Portuguese ("monta uma página com os links", "quero escolher o look e ver as peças") or any other language.
license: MIT
---

# Wardrobe Scout: list

You turn `finds.json` into a page the person keeps open on their phone while they shop.

**Language:** the page is written in the person's language. English and Portuguese labels are built in. For any other language, add a `labels` object to `finds.json` with the same keys as in `${CLAUDE_PLUGIN_ROOT}/scripts/build_list.py` (`eyebrow`, `first_choice`, `open`, `bought`, `breakdown`, `summary`, `summary_note`, `index`, `removed`, `footer`), translated. The newer parts add `looks_index`, `looks_hint`, `look_summary`, `look_summary_one`, `look_none`, `look_done`, `look_owned`, `look_bought`, `show_all`, `sold`, `sold_nodate`, `ask`, `copied` and `copy_failed`.

## Pick by look

When `finds.json` has a `looks` list and each section says which looks it serves (`"looks": ["29", "31"]`), the page opens with a strip of the looks. Tapping one lights up only the sections of its pieces, dims the rest, and says what is left to buy for that look: how many pieces, the total of their first choices with shipping and a link to each. Tapping it again, or "Show all", brings everything back.

- **What is left to buy** updates as the person ticks "Bought": bought pieces leave the total and are listed as bought, and when nothing is left the page says the look is complete.
- **Pieces already theirs** come from `owned` in `finds.json` and are named under each look they serve, at zero cost. Use a look's `note` for anything else worth saying about it.
- A link ending in `#look-<id>` opens the page with that look already picked. Give the person that link for a look they want to send to someone.
- Add looks only when the person has chosen favourites: the strip is for deciding between them, not for every image ever made.

## Message for the seller

An item with `ask` gets a "Message for the seller" button. A tap copies the message (written by `wardrobe-hunt` in the listing's language) and shows it, so the person sees exactly what they will paste in the shop's chat. Where the browser refuses the clipboard, the text is selected for a manual copy. The page never sends anything.

## Build

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_list.py" wardrobe/finds.json wardrobe/shopping-list.html --embed
```

On Windows the command is usually `python` instead of `python3`. `--embed` puts the look photos inside the HTML, so the single file works when the person sends it to their phone. Without it, the photos must stay next to the file.

## Check before handing it over

1. Open the page once (a browser preview or a screenshot) and check at phone width: photos in proportion, nothing cut, prices readable.
2. Read the total of first choices aloud to the person, and how many pieces it covers.
3. If the person's app can publish pages (for example Claude artifacts), offer to publish it so they get a private link for their phone. A page with their face is personal: keep it private unless they decide otherwise.

## When things change

Listings sell. When the person comes back, run the recheck in `wardrobe-hunt` (Step 7): it marks sold listings with `"sold": true` and a date, and the page does the rest on rebuild. Sold listings leave the cards and appear in the section's removed notes, and when a first choice sold, the next listing still for sale takes its place in the totals. Keep the same file name so links on their phone keep working.
