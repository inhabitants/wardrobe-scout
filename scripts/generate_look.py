#!/usr/bin/env python3
"""Dress the person in a new outfit, using their own photos as reference.

Wardrobe Scout never ships an image service of its own. This script calls the
provider the person already has a key for:

  openai  ->  OPENAI_API_KEY  (POST /v1/images/edits, several reference photos)
  gemini  ->  GEMINI_API_KEY  (POST /v1beta/interactions, inline reference photos)
  fal     ->  FAL_KEY         (POST https://fal.run/<model>, photos as data URIs)

Standard library only, so it runs on any Python 3.9+ without installing anything.

Examples:
  python generate_look.py --provider openai --ref me.jpg --ref me2.jpg \
      --prompt-file looks/round-01/01-workwear.txt --out looks/round-01/01-workwear.png
  python generate_look.py --provider gemini --ref me.jpg --prompt "..." --out look.png --dry-run

Change one piece of a look you already like: --edit puts that look first, before
the reference photos, and the prompt says what to change and what to keep.
  python generate_look.py --provider gemini --edit looks/round-02/07-techwear.png \
      --ref me.jpg --prompt-file looks/round-02/07-techwear-boots.txt \
      --out looks/round-02/07-techwear-boots.png

The reference photos leave the computer and go to the chosen provider. Use only
photos of yourself, or of someone who agreed to it.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid

DEFAULT_MODELS = {
    # Check each provider's docs for newer models; any image model that accepts
    # reference images works with --model. Tested for real on 2026-10-27: GPT
    # Image 2.5 kept the person's face closer than Nano Banana 2.1, so fal
    # defaults to it too (a fal key reaches GPT Image 2.5 without an OpenAI key).
    "openai": "gpt-image-2.5-sunburst",
    "gemini": "gemini-nano-banana-2.1",
    "fal": "openai/gpt-image-2.5/sunburst/edit",
}

KEY_ENV = {
    "openai": ["OPENAI_API_KEY"],
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "fal": ["FAL_KEY"],
}

# Portrait sizes per aspect ratio for the OpenAI images API.
OPENAI_SIZES = {"2:3": "1024x1536", "3:4": "1024x1536", "1:1": "1024x1024", "3:2": "1536x1024", "4:3": "1536x1024"}

TIMEOUT = 300


def fail(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def read_key(provider):
    for name in KEY_ENV[provider]:
        value = os.environ.get(name)
        if value:
            return value
    fail(f"no API key found. Set {' or '.join(KEY_ENV[provider])} in your environment.")


def mime_of(path):
    mime, _ = mimetypes.guess_type(path)
    if mime in ("image/jpeg", "image/png", "image/webp"):
        return mime
    with open(path, "rb") as f:
        head = f.read(12)
    if head.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG"):
        return "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    fail(f"{path} is not a JPEG, PNG or WebP image. Convert it first (HEIC photos from phones usually need this).")


def ext_for(data):
    if data.startswith(b"\x89PNG"):
        return ".png"
    if data.startswith(b"\xff\xd8"):
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ""


def post(url, body, headers):
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:2000]
        fail(f"{e.code} from {url}\n{detail}")
    except urllib.error.URLError as e:
        fail(f"could not reach {url}: {e.reason}")


def multipart(fields, files):
    """fields: list of (name, value); files: list of (name, path)."""
    boundary = uuid.uuid4().hex
    out = []
    for name, value in fields:
        out.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    for name, path in files:
        with open(path, "rb") as f:
            data = f.read()
        filename = os.path.basename(path)
        out.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {mime_of(path)}\r\n\r\n".encode() + data + b"\r\n"
        )
    out.append(f"--{boundary}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={boundary}"


def b64_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def find_image(node):
    """Walks a JSON response and returns the first base64 image it finds."""
    if isinstance(node, dict):
        if node.get("type") == "image" and node.get("data"):
            return node["data"]
        if node.get("b64_json"):
            return node["b64_json"]
        inline = node.get("inlineData") or node.get("inline_data")
        if isinstance(inline, dict) and inline.get("data"):
            return inline["data"]
        for value in node.values():
            found = find_image(value)
            if found:
                return found
    elif isinstance(node, list):
        for value in node:
            found = find_image(value)
            if found:
                return found
    return None


def run_openai(args, prompt, key):
    fields = [("model", args.model), ("prompt", prompt), ("size", OPENAI_SIZES.get(args.aspect, "1024x1536"))]
    if args.quality:
        fields.append(("quality", args.quality))
    files = [("image[]", p) for p in args.ref]
    if args.dry_run:
        return {"url": "https://api.openai.com/v1/images/edits", "fields": dict(fields), "images": args.ref}
    body, ctype = multipart(fields, files)
    raw = post("https://api.openai.com/v1/images/edits", body, {"Authorization": f"Bearer {key}", "Content-Type": ctype})
    data = find_image(json.loads(raw))
    if not data:
        fail("the response had no image. Raw start: " + raw[:500].decode("utf-8", "replace"))
    return base64.b64decode(data)


def run_gemini(args, prompt, key):
    payload = {
        "model": args.model,
        "input": [{"type": "text", "text": prompt}]
        + [{"type": "image", "mime_type": mime_of(p), "data": "<base64>" if args.dry_run else b64_file(p)} for p in args.ref],
        "response_format": {"type": "image", "mime_type": "image/jpeg", "aspect_ratio": args.aspect, "image_size": "2K"},
    }
    url = "https://generativelanguage.googleapis.com/v1beta/interactions"
    if args.dry_run:
        return {"url": url, "payload": payload}
    raw = post(url, json.dumps(payload).encode(), {"x-goog-api-key": key, "Content-Type": "application/json"})
    data = find_image(json.loads(raw))
    if not data:
        fail("the response had no image (it may have been blocked by the provider's safety filter). Raw start: "
             + raw[:500].decode("utf-8", "replace"))
    return base64.b64decode(data)


def run_fal(args, prompt, key):
    payload = {
        "prompt": prompt,
        "image_urls": [f"data:{mime_of(p)};base64," + ("<base64>" if args.dry_run else b64_file(p)) for p in args.ref],
        "num_images": 1,
    }
    if args.model.startswith("openai/"):
        # fal's OpenAI models (GPT Image 2.5) take a pixel size, not an aspect ratio.
        width, height = OPENAI_SIZES.get(args.aspect, "1024x1536").split("x")
        payload["image_size"] = {"width": int(width), "height": int(height)}
        if args.quality:
            payload["quality"] = args.quality
    else:
        payload["aspect_ratio"] = args.aspect
    url = f"https://fal.run/{args.model}"
    if args.dry_run:
        return {"url": url, "payload": payload}
    raw = post(url, json.dumps(payload).encode(), {"Authorization": f"Key {key}", "Content-Type": "application/json"})
    resp = json.loads(raw)
    images = resp.get("images") or []
    if not images or not images[0].get("url"):
        fail("the response had no image. Raw start: " + raw[:500].decode("utf-8", "replace"))
    img_url = images[0]["url"]
    if img_url.startswith("data:"):
        return base64.b64decode(img_url.split(",", 1)[1])
    with urllib.request.urlopen(img_url, timeout=TIMEOUT) as r:
        return r.read()


def main():
    p = argparse.ArgumentParser(description="Generate one outfit photo of the person from their reference photos.")
    p.add_argument("--provider", required=True, choices=sorted(DEFAULT_MODELS))
    p.add_argument("--ref", action="append", required=True, help="reference photo of the person (repeat, 1 to 4)")
    p.add_argument("--edit", help="a look image to change one piece of; it goes first, before the reference photos")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", help="the outfit prompt")
    group.add_argument("--prompt-file", help="text file with the outfit prompt")
    p.add_argument("--out", required=True, help="output path; the extension is fixed to match the image format")
    p.add_argument("--model", help="override the default model of the provider")
    p.add_argument("--aspect", default="2:3", help="aspect ratio, default 2:3 (full body, vertical)")
    p.add_argument("--quality", choices=["low", "medium", "high"], help="OpenAI models only (directly or through fal)")
    p.add_argument("--dry-run", action="store_true", help="show the request without sending it or reading the key")
    args = p.parse_args()

    for path in args.ref + ([args.edit] if args.edit else []):
        if not os.path.isfile(path):
            fail(f"image not found: {path}")
    if args.edit:
        # The look being edited goes first: the prompt refers to it as "the first image".
        args.ref = [args.edit] + args.ref
    if not 1 <= len(args.ref) <= 4:
        fail("use between 1 and 4 images in total (the --edit look counts as one).")
    args.model = args.model or DEFAULT_MODELS[args.provider]
    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as f:
            prompt = f.read().strip()
    if not prompt:
        fail("the prompt is empty.")

    key = None if args.dry_run else read_key(args.provider)
    runner = {"openai": run_openai, "gemini": run_gemini, "fal": run_fal}[args.provider]
    result = runner(args, prompt, key)

    if args.dry_run:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    out = args.out
    ext = ext_for(result)
    if ext and not out.lower().endswith(ext) and not (ext == ".jpg" and out.lower().endswith(".jpeg")):
        out = os.path.splitext(out)[0] + ext
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(result)
    print(out)


if __name__ == "__main__":
    main()
