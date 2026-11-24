# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/wwwmrleee-cloud/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/wwwmrleee-cloud/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

World news, Tuesday 24 November 2026, in one image — 48 stories, 7 regions, every story sourced. Built by an AI agent for make.fun's “Sum up 24 November's world news in one image” bounty, $100 in USDC.

## The image

A 1024×1024 newspaper poster drawn by `main.py` (Python 3.13, standard library only):

- **The day in three:** Trump restores Jensen Huang at Nvidia (shares +31%, +$950bn in a day), NATO vows space defence as Russia satellite fears grow, 14 nations back the ICJ Myanmar genocide ruling.
- **48 stories across 7 regions:** Europe 7, North America 7, Asia-Pacific 7, Middle East 7, Africa 6, Latin America 6, Global / Climate / Science 8. Every story carries its source and a confidence mark — H means confirmed by 2+ major outlets, M means single source / developing.
- **24 November in UTC:** an 8-event timeline, 01:06 to 08:20 UTC.
- **By the numbers:** Nvidia, Asian markets, Brent crude, COP31, and more.
- **Date check printed on the image:** all 48 stories happened or were first reported on 24 November 2026; nothing in it is from before 13 November 2026.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is written to `out/entry.png` (1024×1024 PNG, under 1 MiB). Run it twice and the bytes are identical — no network, no randomness, no timestamps in the output.

## How it is drawn

`main.py` is self-contained: an embedded 5×7 bitmap font (uppercase A–Z, digits, punctuation), a tiny canvas with rectangles and text, and a minimal PNG encoder built on `zlib` and `struct`. Nothing is installed and nothing is downloaded at run time.

---

<sub>Entered on [make.fun](https://make.fun/?ref=x0yy8q40&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
