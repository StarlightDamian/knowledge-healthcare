# Open Medical Guide

**0.2.0-online — an online health knowledge library with local search, department navigation and comparison.**

**Live site: [https://www.zengyuwei.cn/healthcare/](https://www.zengyuwei.cn/healthcare/)**

[GitHub repository](https://github.com/StarlightDamian/knowledge-healthcare) · [Personal homepage](https://www.zengyuwei.cn/home/)

[中文](README.md) · [Open the built page](index.html) · [Architecture](docs/architecture.md)

The current repository includes 98 Chinese/English health topics, 14 content dimensions, introductions and knowledge lists, local lexical/BM25 retrieval, and danger-phrase alerts. Navigation has exactly two levels: 11 department groups and 34 populated specialties. Details prioritize danger signs and provide a chapter index. Comparison cells expand to full text; CSV retains all text and line breaks. The top-right language selector preserves filters, search, selection and open details. There are 12 UI locales with explicit English medical-text fallback for 10 of them.

Two additional collections organize the supplied research reports: a cancer map with 34 statistical groups plus two supplementary groups, and a life-course map with 20 shared factors in eight groups. Six disjoint age bands reference the same factors; pregnancy is an additional context. Cancer pages distinguish site, pathology, stage and biomarkers, with evidence and burden context. Links reuse existing condition articles, including breast and colorectal cancer. Each collection keeps its own search query, and department navigation returns to condition topics. See the [MECE mapping](docs/research-mece-map.md), [cancer import record](reports/research-cancer-import.md) and [life-course import record](reports/research-lifecycle-import.md).

Repository content and sources: 98 topics, 1,372 bilingual condition sections and 929 sources; 1,680 project-wide sections. 31 articles completed independent editorial verification: 434 sections and 1677 bilingual claims; 0 clinician sign-offs. P0-04 adds 5 articles and expands 2. P0-04 is published and publicly verified; see [public acceptance evidence](reports/p0-04-release-validation.json). [Historical P0-03 public verification](reports/p0-03-release-validation.json) is retained.

The frozen ICD-11 MMS 2026-01 denominator contains 13,155 eligible categories. Qualified coverage: 131 / 13,155 (0.995819%), leaving 13,024. Target: 100%; milestone: 95%. P0: 130 / 133 complete, 3 remaining and blocked: SAH 8B01.0, 8B01.1 and 8B01.2. Mappings: 131 confirmed, 2 partial, 44 pending. The 188 title-only tasks and 56 map units are separate. See [coverage](reports/icd-coverage.json), [roadmap](docs/coverage-audit-and-roadmap.md) and [priorities](docs/icd-priorities/index.md).

Historical initial batches: Ten of the initial 20 canonical topics passed source cross-checking and independent editorial review; ten retain explicit evidence or content gaps. P0-02 expands meningitis, anaphylaxis and postpartum haemorrhage with 25 bilingual claims across 21 sections; the other 79 articles remain unchanged. Its six candidate categories were reviewed individually: four complete and two partial. At that historical P0-02 release, 33 of 133 P0 categories were complete and 100 remained pending. Nine of the original ten urgent-condition articles are independently verified; carbon monoxide poisoning remains planned. See the [P0 category review](reports/p0-02-icd-scope-review.json) and [historical validation and release record](reports/p0-02-release-validation.json).

Historical P0-03: 19 topics (11 new and eight expanded); its [acceptance](reports/p0-03-acceptance.json) and [public verification](reports/p0-03-release-validation.json) remain unchanged.

Initial confirmed leaf mappings included myocardial infarction BA41.0/BA41.1/BA41.Z, pulmonary embolism BB00.0, and retinal detachment 9B73.0/9B73.3. The [MI scope review](reports/batch-01-mi-icd-scope-review.json) and [PE/retinal scope review](reports/batch-01-pe-retinal-icd-scope-review.json) record the remaining categories and concrete gaps; a shared article does not automatically cover a parent or every descendant.

Read the [online site](https://www.zengyuwei.cn/healthcare/). Git content is validated and imported into immutable PostgreSQL releases; the same-origin API pins one release for the entire browser session. Search terms, age and temperature stay in the browser. Topic access may appear in server logs. Full CSV export remains available; full offline reading is no longer supported.

```bash
python -m pip install -r requirements-runtime.txt -r requirements-dev.txt
python -m src.guide validate
python -m src.guide editorial-audit
python -m src.guide coverage-icd
python -m src.guide priorities-icd
npm test
python -m unittest discover -s tests -p "test_*.py"
python -m src.guide content-audit
python -m src.guide build
# This must fail for the current preview:
python -m src.guide validate --mode clinical
```

For full-schema and real PostgreSQL/HTTP browser tests, install `requirements-dev.txt`, run `python -m playwright install chromium`, then `python -m unittest discover -s tests/e2e -p "test_browser.py"`. The packaged test report explicitly distinguishes in-memory DOM rendering from HTTP/file navigation verification.

The live site is mounted at `/healthcare/` on the existing server and linked from the personal homepage. GitHub stores the source, built page and audit records. Pushes run CI; server updates use a validated candidate and an atomic release switch. See the [deployment guide](docs/deployment.md) for updates and rollback. The static GitHub Pages workflow was removed because it cannot host the required API.

Implementation code is in `/src`; tests in `/tests`. Add content through the validated JSON template, not by editing the generated HTML. The clinical release gate checks recorded attestations, source/text hashes, localization and validation records; it cannot authenticate a clinician or certify regulatory status on its own. Independent governance is required.

Software: MIT. Original prose/data: CC BY 4.0. Third-party sources retain their own rights.
