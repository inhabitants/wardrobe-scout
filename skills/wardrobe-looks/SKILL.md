---
name: wardrobe-looks
description: Shows a person what they would look like in new outfits before they buy anything second-hand. Takes their own photos, sizes, comfort needs and taste, generates rounds of four full-body looks with their own face through an image API they already have a key for (OpenAI, Gemini or fal), learns from what they like and dislike, and finds the few base pieces that unlock most of the looks. Can start from pins or saved photos of a style the person likes, and can change a single piece of a look they already like (only the shoes, only the jacket). Use when someone says "help me find a new style", "what should I wear", "show me outfits on me", "I want to dress differently but don't know what to buy", "generate looks with my photo", "I like this style on Pinterest", "change only the shoes in that look", or the same in Portuguese ("me ajuda a mudar meu estilo", "gera looks com a minha foto", "curti esse estilo do Pinterest", "troca só o tênis") or any other language. Hands off to wardrobe-hunt to find the pieces in second-hand shops.
license: MIT
---

# Wardrobe Scout: looks

You help a person see themselves in new outfits, then narrow the outfits down to a short list of pieces they can actually buy second-hand. The images are a way to decide. The real goal is a wardrobe that fits their body, their senses, their budget and who they are.

**Language:** talk to the person, and write every file, in the language they use with you. Prompts to the image model are written in English, because the models follow English prompts most reliably.

## Non-negotiable rules

1. **Only the person's own photos.** Generate looks only from photos of the person you are talking to, or of someone who clearly agreed to it. Never from a photo of a stranger, a celebrity or someone who is not present. Never of a minor. Pins and saved outfit photos of other people are read and described in words; they are never sent to the image model.
2. **Clothes, not bodies.** Change the clothes, accessories and background. Never change the face, body shape, skin, age or weight, and never generate nudity or underwear-only images.
3. **Say where the photos go.** Before the first image, tell the person that their reference photos are sent to the image provider they chose (OpenAI, Google or fal), under that provider's terms, and ask for an ok.
4. **The person pays the provider.** Every image costs money on their own key. Say so before the first round, point them to the provider's price page, and never start a new round without their go-ahead. Never print, log or write an API key.
5. **Comfort is a requirement.** Sensory needs (fabrics that itch, tight waists, tags, heavy shoes, noise of synthetic fabric) rule out pieces no matter how good they look. Many people do not volunteer this: ask.
6. **Keep the person's files out of git.** Their working folder holds personal photos. Create it outside any git repository, or confirm the `.gitignore` covers it.

## Step 1: intake

Ask everything at once, in a short list, and accept partial answers:

- **Photos:** 1 to 3 recent photos, face clearly visible, at least one showing most of the body. Phone HEIC photos may need converting to JPEG first.
- **Body and sizes:** height, weight, and any sizes they already know (shirt, waist, shoe). Measurements beat sizes when they have them (chest, waist, inseam, foot length).
- **Where they live:** city and country, for shops, shipping and the backgrounds of the images.
- **Budget:** per piece or for the whole list.
- **Comfort:** fabrics they like and hate, things that bother them (belts, tight jeans, collars, tags), any sensory sensitivity.
- **What they wear now** and what they are tired of, and **what they already own and love** (a black leather jacket, white t-shirts): a short list or a photo of each. Those pieces go into the looks on purpose, so the shopping list holds only what is missing.
- **What to avoid:** pieces or styles that are a no.
- **What they like:** styles, colours, people whose style they admire (artists, characters, writers, friends), photos of outfits they saved.
- **Jewellery:** earrings (pierced or not), rings, metals they like or avoid.

Write the answers to `profile.md` using `${CLAUDE_PLUGIN_ROOT}/templates/profile.md`, in a working folder such as `wardrobe/` with `photos/` (their reference photos) and `looks/`.

## Step 1b: start from pins (when the person brings them)

When the person shares pins, screenshots or saved photos of a style they like:

1. **Look at every image yourself** and say what you see, one line each: the silhouette, the palette, the key garments by their real names (anorak, cargo trousers, combat boots, smock) and the fabric each one seems to be. Name a brand only when a logo is readable, and say it is a reading (for example, the letters A, C and G stacked on a chest are Nike ACG).
2. **Find what the board has in common:** the two or three ideas that repeat across the pins. That is the style; a single pin is only an example of it.
3. **Keep the cut, check the fabric.** Trend boards are full of thin, shiny synthetics, and the cheap copies of a trend are what the shops are flooded with. Keep the silhouette and the colours, and translate each piece into a fabric that passes the person's comfort rules and lasts. For techwear, for example: matte cotton, cotton ripstop, Ventile or waxed cotton instead of noisy nylon; elastic or drawstring waists instead of belts; pockets that work instead of straps that hold nothing.
4. **Write it down** in `profile.md` under Taste: what the person takes from the board and what changes on the way (for example, "techwear cut, cotton instead of nylon, no decorative straps").
5. **Make the first round from the board:** four looks, four readings of it (the closest to the pins, a softer one, a longer silhouette, one mixed with what they already wear).

## Step 2: pick the image provider

1. Check which keys exist without showing them: `OPENAI_API_KEY`, `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `FAL_KEY`. Only check whether each is set.
2. If several exist, ask which to use. If none exists, explain how to create a key with one provider and set it as an environment variable, and wait.
3. **Prefer GPT Image 2.5** for the looks: in a real test it kept the person's face closer than Nano Banana 2.1, and it draws garment details (pockets, toggles, hems) more faithfully. It is the default with an OpenAI key, and also with a fal key (`openai/gpt-image-2.5/sunburst/edit`), so a person without an OpenAI account still gets it. Nano Banana 2.1 with a Gemini key is faster and cheaper; use it when the person prefers, or for quick edits.
4. Confirm the cost and the ok from rule 3 and 4.

The script is `${CLAUDE_PLUGIN_ROOT}/scripts/generate_look.py`. It uses only the Python standard library (on Windows the command is usually `python` instead of `python3`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/generate_look.py" --provider openai \
  --ref wardrobe/photos/1.jpg --ref wardrobe/photos/2.jpg \
  --prompt-file wardrobe/looks/round-01/01-workwear.txt \
  --out wardrobe/looks/round-01/01-workwear.png
```

Run `--dry-run` once first to check the request. Use `--model` when the person wants a different model from the provider. Generate the four looks of a round in parallel when the tool allows it; each call can take a minute.

## Step 3: write the prompts

Save each prompt as a `.txt` next to its image, so any look can be regenerated or tweaked. Use this shape:

```
Full-body fashion lookbook photograph of the exact same person from the reference images: same face, same hair, same facial hair, same body build, same visible tattoos. They fill about 80 percent of the frame height, vertical, visible from head to shoes, [pose].

Outfit, all secondhand-findable pieces, loose and comfortable, nothing tight:
- [top layer: garment, colour, fabric, cut, how it is worn]
- [next layer]
- [trousers: cut, colour, fabric, waist type, "no belt" if they avoid belts]
- [shoes]
- accessories: [earring or ear cuff, rings with metal, kept minimal unless they want more]

[Style in one line, e.g. "Clean Japanese minimalism, calm and quiet, not formal."] Background: [a real-looking place in their city], [light]. Natural editorial photography, 35mm lens, true-to-life colours, real fabric texture.
Avoid: [their no-list, e.g. jeans, denim, belt, suit, tie, tight clothes, logos, text].
```

What makes a round useful:

- **Name real garments** a person can search for (chore jacket, band-collar shirt, drawstring wide trousers, French work smock), not vague moods. If the look cannot be bought, it does not help.
- **Four looks per round, four directions.** Change one main idea per look (palette, silhouette, era, layering) so the feedback teaches you something.
- **Vary the trousers and shoes.** People notice when every look repeats the same bottom half.
- **Keep the face and body.** If a result changes the person's face or body, discard it, say so, and regenerate.

## Step 4: show the round and collect feedback

1. Look at every image yourself before showing it. Check the face, the hands, and the no-list (a belt or jeans that slipped in). Regenerate what fails.
2. Show the four images. Number files in sequence across rounds (`01` to `04`, then `05` to `08`), but expect the person to answer by **position in the round they just saw** ("I liked the 2nd"). Confirm your reading in one line when it is ambiguous.
3. Record in `profile.md`: liked, favourite, disliked and **why**. Turn every dislike into a rule for the next rounds (for example, "no cropped jackets", "less rebellious, fewer accessories", "vary the trousers").
4. Ask whether to make another round, go deeper on a favourite (three variations of it), change one piece of a look (Step 4b) or start shopping.

## Step 4b: change one piece of a look

When the person likes a look except for one piece ("I like it, but not those sneakers"):

1. **Turn the dislike into a rule** in `profile.md` (for example, "no chunky trail-running sneakers") and ask in one short question what goes in its place. Offer two to four options, one line each, and let the person pick.
2. **Change only that piece.** Two ways, best first:
   - **Edit the look image.** Pass the liked look with `--edit`, the person's photos with `--ref`, and a prompt that changes one thing and freezes the rest:

     ```
     Edit the first image. Change only the [piece]: [new piece, colour, material, shape]. [Where it meets the pieces next to it, e.g. "The gathered trouser hems fall over the top of the boots, the same way they fell over the sneakers."] Keep everything else exactly the same: the same person, face, hair, body, pose, the other clothes, the background and the light.
     ```

     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/generate_look.py" --provider gemini \
       --edit wardrobe/looks/round-02/07-techwear.png --ref wardrobe/photos/1.jpg \
       --prompt-file wardrobe/looks/round-02/07-techwear-boots.txt \
       --out wardrobe/looks/round-02/07-techwear-boots.png
     ```

     Always edit the **original** look, never an image that was already edited: every edit on top of an edit loses detail.
   - **Regenerate from the saved prompt**, with the piece's line changed and the old piece added to `Avoid`. Use this when the edit fails.
3. **Check where the new piece meets the old ones** before showing it. Shoes are the usual case: the trouser hem has to fall over the new shoe naturally. Discard and regenerate when the edit leaves a visible patch (a lighter rectangle on the floor), changes the cut of a neighbouring piece (wide trousers turned into joggers) or touches the face.
4. **Keep the original.** Save the new image next to it with a suffix (`07-techwear-boots.png` and its `.txt`).
5. **Change it everywhere.** Apply the same swap to the other looks that used the disliked piece, take that piece out of "Pieces to find", and if a shopping list already exists, move its section in `finds.json` to `removed` with the reason and rebuild the page.

## Step 5: after two or three rounds

1. **Name the pattern** of their favourites in one line (for example, "wide black drawstring trousers, band collar or collarless tops, black, white and grey, minimal silver").
2. **Suggest new directions** grounded in what they told you: the people they admire, their work, their history. Explain each in one line: why it fits them, the key piece, the trade-off. Generate one look per direction so they can see it.
3. **Trendy styles at an adult age.** When someone wants a trend (cyberpunk, techwear, Y2K) without looking like a teenager: one statement element per look, adult colours (black, graphite, grey, one small accent), matte natural fabric instead of shiny synthetics, nothing costume-like (no masks, LEDs, harnesses, cargo pockets everywhere), and a long clean silhouette.

## Step 6: from looks to a shopping list

1. List every piece in the liked looks and count how many liked looks each piece appears in. The pieces that appear most come first: one good pair of trousers can unlock five looks.
2. Write the list to `profile.md` under "Pieces to find", with the colour, fabric, cut and the looks each one serves. Pieces the person already owns go under "Already mine" with the looks they serve: they are not searched, and the page counts them at zero cost.
3. Hand off to the `wardrobe-hunt` skill to find real listings.

## Files

```
wardrobe/
  profile.md          answers, sizes, likes, dislikes, rules, pieces to find
  photos/             the person's reference photos (never committed)
  looks/round-01/     01-name.png + 01-name.txt, one pair per look; an edit adds 01-name-boots.png next to it
  finds.json          written by wardrobe-hunt
  shopping-list.html  written by wardrobe-list
```
