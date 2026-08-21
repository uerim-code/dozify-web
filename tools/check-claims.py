#!/usr/bin/env python3
"""Refuse to ship a claim the app cannot back up.

The site has twice drifted ahead of the product: it advertised a titration
planner and a side-effect forecast for weeks after both were removed from the
app, and a visitor who installed on the strength of those sentences got
something else. This is the check that stops the third time.

Two kinds of rule:

  BANNED   — never true of Dozify. A removed feature, or a claim nobody has
             earned (doctor approved, #1, clinically proven). Any hit fails.
  GUARDED  — true in a narrow form and misleading in the broad one. "No ads"
             is the case that matters: the app shows none, but it does measure
             whether an install came from one of our own campaigns, and the
             privacy policy says so. The bare phrase reads as "nothing
             ad-related happens here", which is not what we can promise.

Run: python3 tools/check-claims.py
Exit code 1 on any finding, so it can gate a release.
"""

from __future__ import annotations

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vendored sub-site with its own content; not ours to police.
SKIP_DIRS = ("chembiocalc",)

# Every one of these fires only on the CLAIM, never on the denial of it. The
# first draft matched "not a medical device" and "does not recommend doses" —
# i.e. our own disclaimers — and reported 32 findings in a clean tree. A guard
# that cries wolf is worse than no guard, because the next real hit gets
# skimmed past with the rest.
BANNED: list[tuple[str, str]] = [
    (r"side[- ]effect forecast", "the forecast screen was removed from the app"),
    (r"yan etki tahmini(?! değil)", "the forecast screen was removed from the app"),
    (r"titration planner|titrasyon planlay", "the dose planner was removed; the app records the doctor's plan"),
    # Insulin as a hormone is ordinary article vocabulary. What we must never
    # claim is that Dozify TRACKS it.
    (r"(insulin|insülin)[^.<]{0,40}(track|log|reminder|takip|kaydet|hatırlat)",
     "insulin tracking was deliberately not built"),
    (r"(track|log|takip|kaydet)[^.<]{0,25}(insulin|insülin)",
     "insulin tracking was deliberately not built"),
    (r"doctor[- ]approved|doktor onaylı|doktor tarafından onaylan",
     "no clinician has reviewed this app"),
    (r"clinically proven|klinik olarak kanıtlan", "no clinical evidence exists for the app"),
    (r"#1 (glp|tracker|app)|en iyi glp-?1 uygulama", "an unverifiable superiority claim"),
    # "is a medical device" — not "is not a medical device" / "tıbbi cihaz değildir".
    (r"\bis a (regulated )?medical device\b|(?<!değildir[.,] )tıbbi bir cihazdır",
     "the app is declared NOT a regulated medical device"),
    # "recommends a dose" — not "does not recommend", "önermez", "vermez".
    (r"\b(recommends|suggests) (a |your |the )?dos",
     "the app never recommends a dose"),
    (r"doz öner(?!mez|isi sunmaz|i vermez)(ir|iyor|imiz)", "the app never recommends a dose"),
]

GUARDED: list[tuple[str, str, str]] = [
    (
        r"\bno ads\b|reklam yok(?!,? uygulama)",
        r"no in-app ads|uygulama içinde reklam yok",
        'say "no in-app ads" / "uygulama içinde reklam yok" — install attribution exists and is disclosed in the privacy policy',
    ),
]


def strip_noise(html: str) -> str:
    """Comments and JSON-LD URLs are not user-facing claims."""
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r'https?://[^\s"\'<>]+', " ", html)
    return html


# A phrase in quotation marks, in a sentence that says we do not use it, is the
# editorial policy promising never to claim it: «"doktor onaylı" ... hiçbir
# yerinde görmezsiniz». Reporting that as a banned claim is the same failure as
# the first draft matching our own disclaimers.
DENIAL = re.compile(
    r"\b(görmezsiniz|görmeyeceksiniz|kullanmıyoruz|kullanmaz|yazmıyoruz|yok\b|değil"
    r"|will not see|do not use|does not use|never|nowhere|no page)",
    re.I,
)


def is_quoted(text: str, start: int, end: int) -> bool:
    """True when the hit sits inside quotation marks — a mention, not a use."""
    before, after = text[max(0, start - 3):start], text[end:end + 3]
    return (before.strip().endswith(('"', "“", "«", "'", "\\"))
            and after.strip().startswith(('"', "”", "»", "'", "\\")))


def is_quoted_denial(text: str, start: int, end: int) -> bool:
    """True when the hit is a quoted phrase inside a sentence that rejects it."""
    if not is_quoted(text, start, end):
        return False
    return bool(DENIAL.search(text[max(0, start - 300):end + 300]))


# A percentage is the most quotable thing on a health page and the easiest to
# invent. The app's article library shipped "5-10% get hair loss" (the label
# says 3.3%), "about 25% get constipation" (24% on Wegovy, 3.1% on Ozempic)
# and "more than 80% hit a plateau" (nobody measured that) — all written as
# plain fact, none with a source. The site has so far attributed every figure
# it quotes; this is what keeps that true when the site is edited in a hurry.
#
# The rule is attribution, not an allowlist: the site's numbers come from
# labels AND from studies, so what has to be present is a phrase telling the
# reader where to go and check.
ATTRIBUTION = re.compile(
    r"label|leaflet|product information|trial|stud(y|ies)|cohort|reported in|"
    r"etiket|prospekt[üu]s|[üu]r[üu]n bilgisi|çalışma|kohort|bildiril",
    re.I,
)

PERCENT = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)?\s?%|%\s?\d+(?:[.,]\d+)?")


def visible_text(html: str) -> str:
    """Roughly what a reader sees: tags out, entities left alone."""
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", body)


def unattributed_percentages(html: str) -> list[str]:
    text = visible_text(html)
    # The figures on these pages are decimals — 0.2%, 1.4%, 3.3% — and the
    # separator differs by language: 0.2 in English, 0,2 in Turkish. Treating
    # that dot as the end of a sentence cut every figure in half and reported
    # six clean, correctly attributed sentences as unsourced. Masked here for
    # boundary-finding only; the offsets and the quoted text stay the same.
    flat = re.sub(r"(?<=\d)[.,](?=\d)", "\u0000", text)
    out = []
    for m in PERCENT.finditer(text):
        # The attribution has to be in the same sentence as the figure.
        # A character window does not work here: the pages that quote figures
        # are the pages about labels and trials, so on those the words "label"
        # and "trial" are everywhere, and a ±400 character window found one no
        # matter what. Dropping an invented "roughly 30% of people get a lump"
        # into the injection-site article passed cleanly that way — the very
        # page where an invented figure would do the most damage.
        #
        # Same sentence is also the honest standard. A reader checking a
        # number reads the sentence it is in, not the paragraph four above it.
        start = max(flat.rfind(".", 0, m.start()), flat.rfind("!", 0, m.start()),
                    flat.rfind("?", 0, m.start()), flat.rfind("\n", 0, m.start()))
        end = min((i for i in (flat.find(".", m.end()), flat.find("\n", m.end()))
                   if i != -1), default=len(text))
        sentence = text[start + 1 : end + 1]
        if not ATTRIBUTION.search(sentence):
            out.append(re.sub(r"\s+", " ", sentence).strip())
    return out


def files() -> list[str]:
    out = []
    for path in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(path, ROOT)
        if rel.split(os.sep)[0] in SKIP_DIRS:
            continue
        out.append(rel)
    return sorted(out)


def main() -> int:
    findings: list[str] = []
    checked = files()

    for rel in checked:
        raw = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        text = strip_noise(raw)

        for pattern, why in BANNED:
            for m in re.finditer(pattern, text, re.I):
                if is_quoted_denial(text, m.start(), m.end()):
                    continue
                line = text[: m.start()].count("\n") + 1
                findings.append(f"{rel}:{line}  BANNED  “{m.group(0)}” — {why}")

        for pattern, ok_form, guidance in GUARDED:
            for m in re.finditer(pattern, text, re.I):
                window = text[max(0, m.start() - 120) : m.end() + 120]
                if re.search(ok_form, window, re.I):
                    continue
                # A phrase in quotation marks whose own passage then supplies
                # the precise form is a page explaining the difference, not a
                # page making the vague claim — the privacy guide has a FAQ
                # whose whole subject is that "no ads" says less than people
                # read into it. The block is wider than the window above
                # because a question and its answer are further apart than a
                # sentence, and the precise form has to be present for the
                # exemption to apply at all.
                if is_quoted(text, m.start(), m.end()) and re.search(
                    ok_form, text[max(0, m.start() - 700) : m.end() + 700], re.I
                ):
                    continue
                line = text[: m.start()].count("\n") + 1
                findings.append(f"{rel}:{line}  VAGUE   “{m.group(0)}” — {guidance}")

        for quote in unattributed_percentages(raw):
            line = raw[: raw.find(quote[:20])].count("\n") + 1 if quote[:20] in raw else 0
            findings.append(
                f"{rel}:{line}  UNSOURCED  “…{quote}…” — a percentage with no "
                f"label, trial or study named near it"
            )

    print(f"{len(checked)} sayfa tarandı")
    if not findings:
        print("temiz — yasak iddia yok, belirsiz ifade yok")
        return 0
    print(f"\n{len(findings)} bulgu:\n")
    for f in findings:
        print("  " + f)
    return 1


if __name__ == "__main__":
    sys.exit(main())
