# Agensi listing: Wardrobe Scout

The text for the Agensi form (agensi.io/dashboard, "List Skill"), one field per section, checked against `pack/SKILL.md` and the three skills. The form fills some fields with AI and gets them wrong (it invents a "real run" demo, calls a free skill a "purchase" and makes up capabilities): paste these instead and read every field before sending.

Package: `node pack/pack.mjs` writes `wardrobe-scout.zip` (one top folder, `wardrobe-scout/SKILL.md` inside).

## name

Wardrobe Scout

## summary

See yourself in new outfits before you buy, then find the pieces second-hand in your size, on one shopping list for your phone.

## description

Wardrobe Scout dresses your own photo in new outfits, learns what you like, then looks for the real pieces second-hand, in your size and in fabrics you can wear all day. You end with a short list of checked listings on a page for your phone.

**Three steps**

1. **Looks on your photo.** You share 1 to 3 photos, your sizes, what is comfortable for you and what you like, and pins of a style if you have them. It generates rounds of four full-body looks on your own photo, turns every dislike into a rule, and can change a single piece of a look you like (only the shoes, only the jacket) while keeping the rest of the image.
2. **The hunt.** In your own browser, signed in to your account, it searches Vinted, Depop, Vestiaire Collective and eBay in several languages. It searches the garment, the brand or the fabric instead of the trend word, opens each listing, checks fabric, size, condition and shipping, compares measurements with a garment of yours that fits, skips fast-fashion copies and keeps the three best per piece.
3. **The list.** One page for your phone: every piece with three ranked listings, fit labels and the price with shipping. Tap a look and only its pieces light up, with what is left to buy. Pieces you already own count as zero, and a listing that leaves something out gets a ready question for the seller, in the seller's language, one tap to copy.

**What you need:** Python 3.9 or newer (standard library only), an image API key from OpenAI, Google (Gemini) or fal, and a browser your agent can drive.

**Free and open source (MIT).** Code and project page: https://github.com/inhabitants/wardrobe-scout and https://inhabitants.github.io/wardrobe-scout/

## tags

Pick the closest ones in the form's list, for example lifestyle, shopping, images.

## keywords

fashion, style, outfits, second-hand, thrift, vinted, depop, vestiaire collective, ebay, wardrobe, try-on, gpt image

## requirements

- Python 3.9+
- An image API key: OpenAI, Gemini or fal
- A browser the agent can drive (for example Claude in Chrome or the Claude app's built-in browser)

## permissions

- **hosts:** api.openai.com, generativelanguage.googleapis.com, fal.run (the image provider you pick); the shops you search, in your own browser (vinted, depop.com, vestiairecollective.com, ebay); fonts.googleapis.com and fonts.gstatic.com (the fonts of the list page)
- **file_scopes:** your working folder, `wardrobe/` (photos, looks, profile.md, finds.json, shopping-list.html)
- **tools:** bash, browser
- **notes:** Your photos go only to the image provider you choose, under its terms. Shops open in your own signed-in browser. It never types passwords or card details, never buys and never messages sellers.

## known_limitations

- Never buys, pays, makes offers or messages sellers. It writes the question for the seller; you send it.
- Never types your passwords or card details. You sign in to each shop yourself.
- Does not scrape: one listing at a time, at a human pace, about 40 listings per session.
- Shipping prices show only when you are signed in to the shop.
- Each image is billed by your provider to your own key. Quality depends on the model.
- Only your own photos, or of someone who agreed. Never of a minor. It changes the clothes, never the face or the body.

## usage_example

Install it and say "help me find a new style with my photo". It asks for photos, sizes and what is comfortable, shows a first round of four looks, and moves to the hunt once you pick favourites.

## use_cases

- Change how you dress without buying blind
- Turn a Pinterest board into pieces you can actually wear
- Find mid-range brands second-hand, in real fabrics, at a fair price
- Change one piece of a look you already like
- Keep a shopping list on your phone that tracks what you bought

## sample_input

Here are two photos of me and three Pinterest pins of a style I like. I'm 178 cm and 70 kg, trousers W31 to W32, shoes 43. Cotton only, no belts. Help me find a new style and then the pieces second-hand.

## sample_output

Example of what it produces, based on the fictional example in the repository (Lucas, a synthetic person). This is an illustration, not a recorded run.

- Round 1: four full-body looks on the person's photo, each saved next to the prompt that made it.
- After feedback: the pieces ranked by how many liked looks they unlock, for example "Wide black trousers: 3 of 4 looks".
- For each piece: three second-hand listings with a fit label ("Your size", "Check the waist", "Not cotton"), the price with shipping and a link.
- `shopping-list.html`: a page for the phone where tapping a look shows what is left to buy.

## faq

1. **Is it free?** Yes, MIT. The images are billed by your own provider (OpenAI, Google or fal) to your own key.
2. **Does it buy anything?** No. It never buys, pays, makes offers or messages sellers. You decide and you pay.
3. **Where do my photos go?** Only to the image provider you choose, under its terms. The skill has no server of its own.
4. **Which image model does it use?** GPT Image 2.5 by default with an OpenAI or a fal key, Nano Banana 2.1 with a Gemini key. In our test on a synthetic person, GPT Image 2.5 kept the face closer.
5. **Which shops?** Vinted, Depop, Vestiaire Collective and eBay, opened in your own signed-in browser.
6. **Which languages?** The skill is written in English and answers in the language you use. The list page has English and Portuguese labels built in, and other languages through a labels object.
7. **Can I use someone else's photo?** Only if that person agreed. Never of a minor. It changes clothes, never faces or bodies.
8. **What happens when a listing sells?** Come back and it rechecks the list: sold listings leave, and the next one takes their place.

## compatibility_note

Built and tested in Claude Code, where it also installs as a plugin (`/plugin marketplace add inhabitants/wardrobe-scout`). Any agent that can run Python 3 and drive a browser can follow the package.

## docs_url

https://inhabitants.github.io/wardrobe-scout/

## support_method

Published as is. Questions and bugs go to GitHub issues: https://github.com/inhabitants/wardrobe-scout/issues (no guaranteed reply).

## screenshots

1. https://sapiensinteticos.b-cdn.net/static/free-stuff/wardrobe-scout.webp (Lucas's photo going in, three looks coming out)
2. https://inhabitants.github.io/wardrobe-scout/site/img/list-top.webp (the list on a phone, with a look picked)
3. https://inhabitants.github.io/wardrobe-scout/site/img/look-01.webp
4. https://inhabitants.github.io/wardrobe-scout/site/img/look-02.webp
5. https://inhabitants.github.io/wardrobe-scout/site/img/look-03.webp

## pricing

Free.

## version

0.3.0
