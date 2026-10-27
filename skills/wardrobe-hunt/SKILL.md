---
name: wardrobe-hunt
description: Finds real second-hand listings for the pieces a person wants (from their wardrobe-looks favourites or a list they give you) on Vinted, Depop, Vestiaire Collective and eBay, using the person's own browser while they are signed in. Checks each listing for availability, fabric, colour, size, condition and shipping, ranks three options per piece for the person's body (against the measurements of a garment they own that fits), flags titles that lie about the fabric and fast-fashion copies, drafts a question for the seller in the listing's language for the person to send, rechecks the list later for sold listings, and can hunt for branded pieces priced far below their shop price. Use when someone says "find these on Vinted", "search second-hand for this", "find me good deals on rings", "what would this cost used", or the same in Portuguese ("procura no Vinted", "acha isso usado", "ofertas de anel") or any other language. Never buys anything.
license: MIT
---

# Wardrobe Scout: hunt

You search second-hand shops the way a careful friend would: one listing at a time, reading the details, checking the size against the person's body, and telling them plainly when a listing is not what its title says. The person decides and pays. You never do.

**Language:** talk to the person and write `finds.json` in the language they use with you. Search in several languages (see below).

## Non-negotiable rules

1. **Never buy, never pay, never commit.** Do not click Buy, Pay, Checkout confirmation, Make an offer or Send. Do not message sellers. If the person wants an offer or a question sent to a seller, draft the text and let them send it, or get an explicit ok for that single message.
2. **The person signs in themself.** Open the shop's sign-in page and let them type their own password. Never type a password, a card number or an address.
3. **Browse like a person.** Use the shop's normal pages in the person's browser, at a human pace: open listings one at a time, no more than about 40 listing pages in a session, no hidden APIs, no bulk downloads, no automated messaging. Shops' terms forbid scraping, and this skill is not a scraper.
4. **No seller data.** Save listing links, prices and item details. Never save sellers' names, photos, addresses or messages.
5. **Every claim from the listing itself.** Fabric, size, colour and condition come from the listing page, not from the card title, which is often wrong. Write "not stated" when the listing does not say.
6. **Prices are a snapshot.** Write the date you checked. Listings sell fast; say so.

## Step 1: what to find

Read `profile.md` (from `wardrobe-looks`) for sizes, measurements, comfort rules, budget, country and the "Pieces to find" list, ordered by how many liked looks each piece unlocks. If there is no profile, ask for: the pieces, sizes or measurements, country, budget and the fabrics or details they avoid.

Translate sizes into what listings show:

- **Tops:** the person's usual size fits regular; one size up fits loose; two sizes up fits oversized. Very large sizes on a slim body look like a tent: flag them.
- **Trousers:** waist in inches (W) and in the shop's country size; elastic or drawstring waists forgive a size either way.
- **Shoes:** the person's size, plus the insole length in centimetres for borderline listings. Brands differ: some run large, some list the "true" size in the description.
- **Rings:** inner diameter in millimetres. If the person has not measured: wrap a thread around the finger, measure in millimetres, divide by 3.14.

**Measurements beat size tags.** Ask the person, once, to lay flat one garment of each kind that fits them the way they like (a top, trousers, a jacket) and measure it: pit to pit and length for tops; waist across, inseam and leg opening for trousers; insole length for shoes. These reference measurements go in `profile.md` and are what Step 3 compares listings with.

**Skip what they already own.** Pieces under "Already mine" in `profile.md` are not searched. They go to `owned` in `finds.json` (Step 6), so the page counts them at zero cost.

## Step 2: search

Open the shop in the browser and ask the person to sign in, so listings show the real shipping to their address. Then, for each piece:

1. Search with the piece's real name in **several languages**. On Vinted, listings from other countries keep their original titles, so a black band-collar shirt is also `chemise col mao noir`, `camisa cuello mao negra`, `camicia collo coreana nera`, `grandad collar shirt black`.
2. **Search the garment, the brand or the fabric, never the trend word.** "Techwear", "cyberpunk" or "Y2K" in the search box pulls in mostly fast-fashion copies. Search the real piece (`cargo ripstop`, `anorak`, `smock`), the fabric (`Ventile`, `waxed cotton`, `Gore-Tex`, `Cordura`, `merino`) or brands that make the piece well, with the colour filter on.
3. Filter by the person's sizes. Read the size, brand, condition and price from each result card.
4. Shortlist 4 to 6 candidates per piece that look right in the photo and in the card.

The search pages, quirks and fees of each shop are in `${CLAUDE_PLUGIN_ROOT}/skills/wardrobe-hunt/stores.md`. Read it before searching a shop for the first time.

## Step 3: check each listing

Open every shortlisted listing and record:

- **Still available?** Sold, reserved or removed listings leave the list. Note "sold" so the person knows why it disappeared.
- **Fabric** from the listing details. A title that says "cotton" with details that say "polyester and wool" is common: flag it.
- **Colour, size, condition**, and **measurements** if the seller gives them (or a note to ask for them).
- **Measurements against the reference.** When the listing gives flat measurements, compare them with the person's reference garment. Within about 2 cm is `ok`. More than that is `warn`, with the difference in the note ("waist 3 cm narrower than your reference pair"); for a loose style, larger than the reference is fine up to the looseness the person wants. Put both numbers in `specs`, for example `["Waist, flat", "37 cm (yours 38)"]`.
- **Price** as shown, with the buyer fee when the shop adds one, and the **cheapest shipping** to the person.
- **Problems the seller mentions:** stains, missing insole, repairs, "fits small".
- **Signs of a fast-fashion copy**, common when the style is a trend: no brand or an invented one, thin shiny "100% polyester", straps and buckles that hold nothing, random printed lettering, unbranded plastic zips, catalogue photos on a white background, and the same listing "new with tags" in every size. Drop those, or keep one as `bad` with the reason when the person asked about that kind of piece.

**A message for the seller.** When something only the seller can answer is missing (the composition label, flat measurements, insole length, a photo of the sole or of the zip), write the question in the item's `ask`, in the **language of the listing** (a French listing gets French), short and polite, with no personal data, ending with a thanks. The page turns it into a copy button; the person sends it themself. For example:

```
Bonjour ! Pourriez-vous m'envoyer une photo de l'étiquette de composition et les mesures à plat (aisselle à aisselle et longueur) ? Merci beaucoup !
```

If a listing page comes back empty in the browser, the page may not render while the browser window is hidden: bring the browser to the front or take a screenshot, then read it again.

When you cannot judge something only a photo shows (how thick a sole is, how loose a cut is), look at the listing's main photo before ranking it.

## Step 4: rank

Per piece, keep three listings, best first:

1. Fits the person and their comfort rules.
2. Matches the look (colour, cut, fabric).
3. Condition.
4. Total price with shipping.

Give each a fit label the person can read at a glance: **ok** (fits), **warn** (check something: waist, insole, size tag), **bad** (too big, wrong fabric, kept only to explain), **info** (depends on a measurement, like rings).

When the person wants "just one, the one worth it" for a piece, give one and say why it is the one.

## Step 5: deals (optional)

When the person asks for branded pieces far below their price, search brand names in the category (for rings: steel and silver jewellery brands; for shoes: well-known makers). For each candidate:

1. Find the brand's current shop price with a web search, and cite the source.
2. Compare it with the listing's total. Only call it a deal when the gap is large, and say how you know.
3. Respect the person's material rules (for example "silver only when it is worth it; prefer stainless steel or titanium, which do not tarnish").

## Step 6: write finds.json

Write `finds.json` in the person's working folder, following `${CLAUDE_PLUGIN_ROOT}/examples/finds.example.json`:

- `lang`, `title`, `intro`, `checked` (date), `currency`.
- `body`: rows like `["Body", "178 cm · 70 kg"]`, `["Shoes", "43"]`.
- `looks` (optional, for the look picker): the favourite looks, each with `id`, `image` (relative to `finds.json`), `alt`, optional `caption` and `note`.
- `owned` (optional): pieces the person already has, each with `title` and `looks`. The page names them under each look as already theirs, at zero cost.
- `sections`: one per piece, with `id`, `title`, `short` (for the index), `text`, optional `image` (path to the look that uses it, relative to `finds.json`), `looks` (the ids of the looks this piece serves), `items` (three ranked listings) and `removed` (what left the list and why).
- Each item: `id`, `title`, `fit`, `fit_label`, `first_choice`, `specs` (pairs), `note`, `price`, `shipping`, `url`, `store`, and optionally `ask` (the message for the seller) and `sold` with `sold_on` (Step 7).

Then hand off to `wardrobe-list` to build the page.

## Step 7: recheck (when the person comes back)

Listings sell in days. When the person returns to the list, or before they start buying:

1. Open every first choice, then the other listings, at the same human pace as Step 2.
2. A listing that sold, is reserved or was removed gets `"sold": true` and `"sold_on": "<date>"`. Do not delete it: the page moves it to the section's removed notes, and the next listing still for sale becomes the first choice on its own.
3. A changed price or shipping gets updated, with a word in the note when it went up.
4. A piece with no listing left gets a new search for that piece only.
5. Update `checked` to today and rebuild the page with `wardrobe-list`, under the same file name.
