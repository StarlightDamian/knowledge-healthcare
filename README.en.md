# Open Medical Guide

**0.1.0-preview — a self-contained health knowledge library with local search, department navigation and comparison.**

**Live site: [https://www.zengyuwei.cn/healthcare/](https://www.zengyuwei.cn/healthcare/)**

[GitHub repository](https://github.com/StarlightDamian/knowledge-healthcare) · [Personal homepage](https://www.zengyuwei.cn/home/)

[中文](README.md) · [Open the built page](index.html) · [Architecture](docs/architecture.md)

Included: 72 Chinese/English health topics, 14 content dimensions, introductions and knowledge lists, local lexical/BM25 retrieval, and danger-phrase alerts. Navigation has exactly two levels: 11 department groups and 32 populated specialties. Details prioritize danger signs and provide a chapter index. Comparison cells expand to full text; CSV retains all text and line breaks. The top-right language selector preserves filters, search, selection and open details. There are 12 UI locales with explicit English medical-text fallback for 10 of them.

Two additional collections organize the supplied research reports: a cancer map with 34 statistical groups plus two supplementary groups, and a life-course map with 20 shared factors in eight groups. Six disjoint age bands reference the same factors; pregnancy is an additional context. Cancer pages distinguish site, pathology, stage and biomarkers, with evidence and burden context. Links reuse existing condition articles, including breast and colorectal cancer. Each collection keeps its own search query, and department navigation returns to condition topics. See the [MECE mapping](docs/research-mece-map.md), [cancer import record](reports/research-cancer-import.md) and [life-course import record](reports/research-lifecycle-import.md).

Content and sources: 72 topics (67 conditions or health concerns and five symptom entries), 1,008 bilingual sections and 303 source records. Independent medical review, translation review and clinical validation of alert rules are pending. There are zero clinician-approved topics and zero sections with completed independent claim verification. The page explains these facts in “Content and sources”; each topic provides an expandable “Sources and editorial information” panel and section-level references. [Editorial records](reports/content-expansion/) identify inspected sources and relevant sections. Three trial cards contain abstract-level summaries; a fourth contains bibliographic metadata.

The 95% coverage review has not passed; exact coverage remains `null`. The denominator is eligible independent condition categories in ICD-11 MMS 2026-01. The full snapshot and category mappings are pending. The 198 title-only tasks and 56 knowledge-map units are counted separately from complete condition articles and do not raise the coverage numerator. Ten known urgent gaps and the order of work are saved in the [coverage roadmap](docs/coverage-audit-and-roadmap.md) and [coverage review data](reports/coverage-review.json). See also the [writing audit](reports/anti-defensive-writing-audit.md).

Open `index.html`, or run `python -m http.server 8000` from the repository root. No external CSS, fonts, JS, inference API or query analytics are required. The source records are embedded. Manually following a reference visits a third-party website; hosting providers may keep normal access logs.

```bash
python -m src.guide validate
npm test
python -m unittest discover -s tests -p "test_*.py"
python -m src.guide content-audit
python -m src.guide build
# This must fail for the current preview:
python -m src.guide validate --mode clinical
```

For optional full-schema and browser tests, install `requirements-dev.txt`, run `python -m playwright install chromium`, then `python -m unittest discover -s tests/e2e -p "test_browser.py"`. The packaged test report explicitly distinguishes in-memory DOM rendering from HTTP/file navigation verification.

The live site is mounted at `/healthcare/` on the existing server and linked from the personal homepage. GitHub stores the source, built page and audit records. Pushes run CI; server updates use a validated candidate and an atomic release switch. See the [deployment guide](docs/deployment.md) for updates and rollback. The manual GitHub Pages workflow remains an optional alternative.

Implementation code is in `/src`; tests in `/tests`. Add content through the validated JSON template, not by editing the generated HTML. The clinical release gate checks recorded attestations, source/text hashes, localization and validation records; it cannot authenticate a clinician or certify regulatory status on its own. Independent governance is required.

Software: MIT. Original prose/data: CC BY 4.0. Third-party sources retain their own rights.
