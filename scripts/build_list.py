#!/usr/bin/env python3
"""Turn finds.json into a shopping list page you can open on your phone.

  python build_list.py finds.json shopping-list.html [--embed]

--embed puts the look photos inside the HTML, so the single file works anywhere
(send it to yourself, open it offline). Without it, photo paths stay relative.

Standard library only. The page is plain HTML and CSS, with a little JavaScript:
- the "bought" boxes, saved only in the browser that ticks them;
- the look picker: when finds.json has "looks", tapping a look lights up only the
  pieces it uses, with what is left to buy (pieces already owned or ticked as
  bought do not count). A link ending in #look-<id> opens with that look picked;
- the seller message: an item with "ask" gets a button that copies a ready
  message in the seller's language. The person sends it; the page never does.

Items marked "sold": true leave the cards and show up in the section's
"removed" notes; when the first choice sold, the next listing takes its place.
"""

import argparse
import base64
import html
import json
import mimetypes
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(HERE, "..", "templates", "shopping-list.css")

LABELS = {
    "en": {
        "eyebrow": "{stores} · checked while signed in on {date}",
        "first_choice": "1st choice",
        "open": "Open on {store}",
        "bought": "Bought",
        "breakdown": "{price} + shipping {ship}",
        "summary": "First choice of each of the {n} pieces, with shipping",
        "summary_note": "Each seller charges their own shipping. Prices use the cheapest shipping each listing shows.",
        "index": "Pieces",
        "removed": "Removed from the list: ",
        "footer": "Listings sell fast. The \"Bought\" boxes are saved only on this device.",
        "looks_index": "Looks",
        "looks_hint": "Tap a look to light up only its pieces.",
        "look_summary": "{n} pieces to buy, first choices {total} with shipping:",
        "look_summary_one": "1 piece to buy, first choice {total} with shipping:",
        "look_none": "No piece of this look is on the list yet.",
        "look_done": "Everything this look needs is bought.",
        "look_owned": "Already yours: {list}.",
        "look_bought": "Bought: {list}.",
        "show_all": "Show all",
        "sold": "{title}, sold on {date}.",
        "sold_nodate": "{title}, sold.",
        "ask": "Message for the seller",
        "copied": "Copied. Paste it in the chat with the seller.",
        "copy_failed": "Select the text and copy it.",
    },
    "pt": {
        "eyebrow": "{stores} · conferido logado em {date}",
        "first_choice": "1ª escolha",
        "open": "Abrir no {store}",
        "bought": "Comprei",
        "breakdown": "{price} + envio {ship}",
        "summary": "Primeira escolha de cada uma das {n} peças, com envio",
        "summary_note": "Cada vendedor cobra o próprio envio. Usei o envio mais barato que cada anúncio mostra.",
        "index": "Peças",
        "removed": "Saiu da lista: ",
        "footer": "Anúncios saem do ar rápido. As caixas \"Comprei\" ficam salvas só neste aparelho.",
        "looks_index": "Looks",
        "looks_hint": "Toca num look pra acender só as peças dele.",
        "look_summary": "{n} peças pra comprar, primeiras escolhas {total} com envio:",
        "look_summary_one": "1 peça pra comprar, primeira escolha {total} com envio:",
        "look_none": "Nenhuma peça deste look está na lista ainda.",
        "look_done": "Tudo que este look pede já foi comprado.",
        "look_owned": "Já é seu: {list}.",
        "look_bought": "Comprado: {list}.",
        "show_all": "Ver todos",
        "sold": "{title}, vendido em {date}.",
        "sold_nodate": "{title}, vendido.",
        "ask": "Mensagem pro vendedor",
        "copied": "Copiado. Cola no chat com o vendedor.",
        "copy_failed": "Seleciona o texto e copia.",
    },
}

SYMBOLS = {"EUR": "€", "GBP": "£", "USD": "$", "BRL": "R$", "CHF": "CHF", "SEK": "kr", "DKK": "kr", "PLN": "zł"}


def esc(text):
    return html.escape(str(text), quote=True)


def money(value, lang, currency, symbol=True):
    english = lang.startswith("en")
    number = f"{value:,.2f}"
    if not english:
        number = number.replace(",", "X").replace(".", ",").replace("X", ".")
    if not symbol:
        return number
    sym = SYMBOLS.get(currency, currency)
    return f"{sym}{number}" if english and len(sym) == 1 else f"{number} {sym}"


def slug(value):
    return re.sub(r"[^a-z0-9-]", "-", str(value).lower())


def item_total(item):
    return float(item["price"]) + float(item.get("shipping", 0))


def listings(sec):
    """The section's listings that are still for sale, with a first choice.

    A sold listing leaves the cards. When the first choice sold, the next one
    still for sale takes its place, so the totals keep making sense.
    """
    items = sec.get("items", [])
    live = [dict(i) for i in items if not i.get("sold")]
    if live and not any(i.get("first_choice") for i in live):
        live[0]["first_choice"] = True
    return live, [i for i in items if i.get("sold")]


def first_choice(sec):
    live, _ = listings(sec)
    return next((i for i in live if i.get("first_choice")), None)


def image_src(path, base_dir, embed):
    if not path:
        return None
    full = path if os.path.isabs(path) else os.path.join(base_dir, path)
    if embed:
        if not os.path.isfile(full):
            print(f"warning: image not found, skipped: {full}", file=sys.stderr)
            return None
        mime = mimetypes.guess_type(full)[0] or "image/jpeg"
        with open(full, "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")
    return path.replace("\\", "/")


def card(item, lang, currency, labels):
    specs = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in item.get("specs", []))
    pick = f'<span class="pick">{esc(labels["first_choice"])}</span>' if item.get("first_choice") else ""
    breakdown = labels["breakdown"].format(
        price=money(float(item["price"]), lang, currency, symbol=False),
        ship=money(float(item.get("shipping", 0)), lang, currency, symbol=False),
    )
    store = item.get("store", "Vinted")
    cid = slug(item["id"])
    note = f'<p class="nota">{esc(item["note"])}</p>' if item.get("note") else ""
    ask = ""
    if item.get("ask"):
        ask = (f'        <div class="ask"><button type="button" class="ask-copy" aria-controls="ask-{cid}" '
               f'aria-expanded="false">{esc(labels["ask"])}</button>'
               f'<p class="ask-text" id="ask-{cid}" hidden>{esc(item["ask"])}</p></div>\n')
    return f"""      <li class="tag" data-id="{cid}">
        <div class="tag-top"><span class="fit {esc(item.get('fit', 'info'))}">{esc(item.get('fit_label', ''))}</span>{pick}</div>
        <h3>{esc(item['title'])}</h3>
        <dl class="specs">{specs}</dl>
        {note}
        <div class="tag-foot">
          <p class="price">{esc(money(item_total(item), lang, currency))}<small>{esc(breakdown)}</small></p>
          <a class="open" href="{esc(item['url'])}" target="_blank" rel="noopener">{esc(labels['open'].format(store=store))}</a>
        </div>
{ask}        <label class="got" for="got-{cid}"><input type="checkbox" id="got-{cid}"> {esc(labels['bought'])}</label>
      </li>
"""


def section(sec, lang, currency, labels, base_dir, embed):
    src = image_src(sec.get("image"), base_dir, embed)
    text = f"<p>{esc(sec['text'])}</p>" if sec.get("text") else ""
    if src:
        head = f"""    <div class="cat-head">
      <figure>
        <img src="{esc(src)}" alt="{esc(sec.get('image_alt', ''))}" width="420" height="630">
        <figcaption>{esc(sec.get('image_caption', ''))}</figcaption>
      </figure>
      <div><h2>{esc(sec['title'])}</h2>{text}</div>
    </div>
"""
    else:
        head = f"""    <div class="cat-head sem-foto">
      <div><h2>{esc(sec['title'])}</h2>{text}</div>
    </div>
"""
    steps = ""
    if sec.get("steps"):
        steps = '    <ol class="medir">' + "".join(f"<li>{esc(s)}</li>" for s in sec["steps"]) + "</ol>\n"
    live, sold = listings(sec)
    cards = "".join(card(i, lang, currency, labels) for i in live)
    notes = "".join(f'    <p class="saiu">{esc(n)}</p>\n' for n in sec.get("notes", []))
    gone = list(sec.get("removed", []))
    for i in sold:
        key = "sold" if i.get("sold_on") else "sold_nodate"
        gone.append(labels[key].format(title=i["title"], date=i.get("sold_on", "")))
    notes += "".join(f'    <p class="saiu">{esc(labels["removed"])}{esc(r)}</p>\n' for r in gone)
    looks = " ".join(slug(x) for x in sec.get("looks", []))
    data_looks = f' data-looks="{esc(looks)}"' if looks else ""
    return f"""  <section class="cat" id="{esc(sec['id'])}"{data_looks}>
{head}{steps}    <ul class="tags">
{cards}    </ul>
{notes}  </section>
"""


def looks_block(data, sections, labels, base_dir, embed):
    """The look picker: one button per look, and what each look needs.

    Returns the HTML and the data the page script uses to say what is left to
    buy, which changes as the person ticks "bought".
    """
    looks = data.get("looks", [])
    if not looks:
        return "", {}
    owned = data.get("owned", [])
    buttons, info = [], {}
    for look in looks:
        key = slug(look["id"])
        caption = look.get("caption") or f"Look {look['id']}"
        src = image_src(look.get("image"), base_dir, embed)
        img = f'<img src="{esc(src)}" alt="{esc(look.get("alt", caption))}" width="420" height="630">' if src else ""
        buttons.append(f'      <li><button type="button" class="look-pick" id="look-{esc(key)}" data-look="{esc(key)}" '
                       f'aria-pressed="false">{img}<span>{esc(caption)}</span></button></li>\n')
        pieces = []
        for s in sections:
            if key not in {slug(x) for x in s.get("looks", [])}:
                continue
            first = first_choice(s)
            if first:
                pieces.append({"sec": s["id"], "name": s.get("short", s["title"]), "price": round(item_total(first), 2)})
        mine = [o["title"] for o in owned if key in {slug(x) for x in o.get("looks", [])}]
        info[key] = {"caption": caption, "note": look.get("note", ""), "pieces": pieces, "owned": mine}
    block = (f'  <section class="looks-pick" id="looks" aria-label="{esc(labels["looks_index"])}">\n'
             f'    <ul class="looks">\n{"".join(buttons)}    </ul>\n'
             f'    <p class="escolha" id="escolha" aria-live="polite">{esc(labels["looks_hint"])}</p>\n'
             f'  </section>\n')
    return block, info


def script_json(value):
    # Inside <script>, "</" must not close the tag early.
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build(data, base_dir, embed):
    lang = data.get("lang", "en")
    labels = dict(LABELS["pt" if lang.startswith("pt") else "en"])
    labels.update(data.get("labels", {}))
    currency = data.get("currency", "EUR")
    sections = data.get("sections", [])

    firsts = [f for f in (first_choice(s) for s in sections) if f]
    first_total = sum(item_total(i) for i in firsts)
    stores = sorted({i.get("store", "Vinted") for s in sections for i in s.get("items", [])})

    body_rows = data.get("body", [])
    medidas = ""
    if body_rows:
        cells = []
        for n, (k, v) in enumerate(body_rows):
            cls = ' class="corpo"' if n == 0 else ""
            cells.append(f"<div{cls}><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>")
        medidas = '    <dl class="medidas">' + "".join(cells) + "</dl>\n"

    resumo = ""
    if firsts:
        resumo = (f'    <p class="resumo"><span>{esc(labels["summary"].format(n=len(firsts)))}</span>'
                  f'<strong>{esc(money(first_total, lang, currency))}</strong>'
                  f'<span>{esc(labels["summary_note"])}</span></p>\n')

    picker, looks_info = looks_block(data, sections, labels, base_dir, embed)

    nav = ""
    if len(sections) + (1 if picker else 0) > 3:
        links = f'<a href="#looks">{esc(labels["looks_index"])}</a>' if picker else ""
        links += "".join(f'<a href="#{esc(s["id"])}">{esc(s.get("short", s["title"]))}</a>' for s in sections)
        nav = f'    <nav class="indice" aria-label="{esc(labels["index"])}">{links}</nav>\n'

    closing = ""
    if data.get("closing"):
        c = data["closing"]
        paras = "".join(f"<p>{esc(p)}</p>" for p in c.get("paragraphs", []))
        closing = f'  <section class="proximo"><h2>{esc(c.get("title", ""))}</h2>{paras}</section>\n'

    with open(CSS_PATH, encoding="utf-8") as f:
        css = f.read()
    title = data.get("title", "Shopping list")
    key = "wardrobe-scout-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    eyebrow = labels["eyebrow"].format(stores=" · ".join(stores), date=data.get("checked", ""))
    intro = f'    <p class="lede">{esc(data["intro"])}</p>\n' if data.get("intro") else ""
    secs = "\n".join(section(s, lang, currency, labels, base_dir, embed) for s in sections)
    page_labels = {k: labels[k] for k in ("look_summary", "look_summary_one", "look_none", "look_done",
                                          "look_owned", "look_bought", "show_all", "ask", "copied", "copy_failed")}
    money_fmt = {"english": lang.startswith("en"), "symbol": SYMBOLS.get(currency, currency)}

    return f"""<!doctype html>
<html lang="{esc(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Shippori+Mincho:wght@600;800&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<style>
body {{ margin: 0; }}
img {{ max-width: 100%; }}
{css}</style>
</head>
<body>
<main class="wrap">
  <header class="top">
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h1>{esc(title)}</h1>
{intro}{medidas}{resumo}{nav}  </header>

{picker}
{secs}
{closing}
  <p class="rodape">{esc(labels['footer'])}</p>
</main>
<script>
(function () {{
  var KEY = {json.dumps(key)};
  var state = {{}};
  try {{ state = JSON.parse(localStorage.getItem(KEY) || "{{}}") || {{}}; }} catch (e) {{ state = {{}}; }}
  document.querySelectorAll(".tag").forEach(function (tag) {{
    var id = tag.getAttribute("data-id");
    var box = tag.querySelector(".got input");
    if (!box) return;
    box.checked = !!state[id];
    tag.classList.toggle("is-got", box.checked);
    box.addEventListener("change", function () {{
      state[id] = box.checked;
      tag.classList.toggle("is-got", box.checked);
      try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}}
    }});
  }});
}})();

(function () {{
  var L = {script_json(page_labels)};
  var M = {script_json(money_fmt)};
  var LOOKS = {script_json(looks_info)};

  // Seller message: copy it, and show it so the person sees what they will send.
  document.querySelectorAll(".ask-copy").forEach(function (btn) {{
    var text = document.getElementById(btn.getAttribute("aria-controls"));
    btn.addEventListener("click", function () {{
      text.hidden = false;
      btn.setAttribute("aria-expanded", "true");
      function done(msg) {{
        btn.textContent = msg;
        setTimeout(function () {{ btn.textContent = L.ask; }}, 2500);
      }}
      function fallback() {{
        var range = document.createRange();
        range.selectNodeContents(text);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        done(L.copy_failed);
      }}
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text.textContent).then(function () {{ done(L.copied); }}, fallback);
      }} else {{
        fallback();
      }}
    }});
  }});

  var main = document.querySelector("main");
  var out = document.getElementById("escolha");
  if (!out) return;
  var HINT = out.innerHTML;
  var picks = document.querySelectorAll(".look-pick");
  var cats = document.querySelectorAll(".cat");

  function esc(s) {{
    return String(s).replace(/[&<>"']/g, function (c) {{
      return {{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }}[c];
    }});
  }}
  function money(v) {{
    var parts = v.toFixed(2).split(".");
    var whole = parts[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, M.english ? "," : ".");
    var num = whole + (M.english ? "." : ",") + parts[1];
    return M.english && M.symbol.length === 1 ? M.symbol + num : num + " " + M.symbol;
  }}
  function bought(secId) {{
    var sec = document.getElementById(secId);
    return !!(sec && sec.querySelector(".tag.is-got"));
  }}
  function summary(look) {{
    var d = LOOKS[look];
    var left = d.pieces.filter(function (p) {{ return !bought(p.sec); }});
    var got = d.pieces.filter(function (p) {{ return bought(p.sec); }});
    var link = function (p) {{ return '<a href="#' + esc(p.sec) + '">' + esc(p.name) + "</a>"; }};
    var parts = ["<strong>" + esc(d.caption) + "</strong>"];
    if (left.length) {{
      var total = left.reduce(function (s, p) {{ return s + p.price; }}, 0);
      var head = (left.length === 1 ? L.look_summary_one : L.look_summary)
        .replace("{{n}}", left.length).replace("{{total}}", money(total));
      parts.push("<span>" + esc(head) + " " + left.map(link).join(", ") + ".</span>");
    }} else {{
      parts.push("<span>" + esc(d.pieces.length ? L.look_done : L.look_none) + "</span>");
    }}
    if (got.length) parts.push("<span>" + esc(L.look_bought).replace("{{list}}", got.map(link).join(", ")) + "</span>");
    if (d.owned.length) parts.push("<span>" + esc(L.look_owned.replace("{{list}}", d.owned.join(", "))) + "</span>");
    if (d.note) parts.push("<span>" + esc(d.note) + "</span>");
    return parts.join(" ");
  }}
  function pick(look) {{
    if (look) main.setAttribute("data-sel", look); else main.removeAttribute("data-sel");
    picks.forEach(function (b) {{ b.setAttribute("aria-pressed", String(b.getAttribute("data-look") === look)); }});
    cats.forEach(function (c) {{
      var uses = (" " + (c.getAttribute("data-looks") || "") + " ").indexOf(" " + look + " ") !== -1;
      c.classList.toggle("on", !!look && uses);
    }});
    if (!look) {{ out.innerHTML = HINT; return; }}
    out.innerHTML = summary(look) + ' <button type="button" id="ver-todos"></button>';
    var all = document.getElementById("ver-todos");
    all.textContent = L.show_all;
    all.addEventListener("click", function () {{ pick(null); }});
  }}
  picks.forEach(function (b) {{
    b.addEventListener("click", function () {{
      var look = b.getAttribute("data-look");
      pick(main.getAttribute("data-sel") === look ? null : look);
    }});
  }});
  document.querySelectorAll(".got input").forEach(function (box) {{
    box.addEventListener("change", function () {{
      var look = main.getAttribute("data-sel");
      if (look) pick(look);
    }});
  }});
  var start = (location.hash || "").replace(/^#look-/, "");
  if (start && LOOKS[start]) pick(start);
}})();
</script>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description="Build the shopping list page from finds.json.")
    p.add_argument("finds", help="path to finds.json")
    p.add_argument("out", help="output HTML file")
    p.add_argument("--embed", action="store_true", help="embed the look photos in the HTML")
    args = p.parse_args()
    with open(args.finds, encoding="utf-8") as f:
        data = json.load(f)
    page = build(data, os.path.dirname(os.path.abspath(args.finds)), args.embed)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(page)
    print(args.out)


if __name__ == "__main__":
    main()
