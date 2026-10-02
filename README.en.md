# Open Medical Guide

**0.2.0-online — an online health knowledge library with local search, department navigation and comparison.**

**Live site: [https://www.zengyuwei.cn/healthcare/](https://www.zengyuwei.cn/healthcare/)**

[GitHub repository](https://github.com/StarlightDamian/knowledge-healthcare) · [Personal homepage](https://www.zengyuwei.cn/home/)

[中文](README.md) · [Open the built page](index.html) · [Architecture](docs/architecture.md)

The current repository includes 77 Chinese/English health topics, 14 content dimensions, introductions and knowledge lists, local lexical/BM25 retrieval, and danger-phrase alerts. Navigation has exactly two levels: 11 department groups and 33 populated specialties. Details prioritize danger signs and provide a chapter index. Comparison cells expand to full text; CSV retains all text and line breaks. The top-right language selector preserves filters, search, selection and open details. There are 12 UI locales with explicit English medical-text fallback for 10 of them.

Two additional collections organize the supplied research reports: a cancer map with 34 statistical groups plus two supplementary groups, and a life-course map with 20 shared factors in eight groups. Six disjoint age bands reference the same factors; pregnancy is an additional context. Cancer pages distinguish site, pathology, stage and biomarkers, with evidence and burden context. Links reuse existing condition articles, including breast and colorectal cancer. Each collection keeps its own search query, and department navigation returns to condition topics. See the [MECE mapping](docs/research-mece-map.md), [cancer import record](reports/research-cancer-import.md) and [life-course import record](reports/research-lifecycle-import.md).

Repository content and sources: 77 topics (72 conditions or health concerns and five symptom entries), 1,078 bilingual condition sections and 461 source records. The project-wide editorial scope contains 1,386 sections, including modules, map summaries and life-course introductions. Independent medical review, translation review and clinical validation of alert rules are pending. There are zero clinician-approved topics and five articles with completed independent claim verification: 70 sections and 321 bilingual claims (myocardial infarction 90, pulmonary embolism 55, retinal detachment 68, obstructive sleep apnea 52 and testicular torsion 56). The page explains these facts in “Content and sources”; each topic provides an expandable “Sources and editorial information” panel and section-level references. [Editorial records](reports/content-expansion/) identify inspected sources and relevant sections. Three trial cards contain abstract-level summaries; a fourth contains bibliographic metadata.

The frozen ICD-11 MMS 2026-01 denominator contains 13,155 eligible independent categories. Fully evidence-qualified category coverage is currently 8 / 13,155 (approximately 0.060813%), leaving 13,147 categories unqualified. The final target is all 13,155 categories (100%); 95%, or 12,498 qualified categories, is an intermediate milestone. Mapping states are eight confirmed, five partial and 47 pending. This measures completion of the new evidence and mapping standard, not the usefulness of existing articles or the percentage of real patients covered. The 193 title-only tasks and 56 map units remain separate. See the [coverage report](reports/icd-coverage.json), [roadmap](docs/coverage-audit-and-roadmap.md), [complete priority list](docs/icd-priorities/index.md) and [full CSV](reports/icd-priorities.csv). Each eligible category has an initial editorial priority, rationale, evidence scope and a place in the remaining-work queue. Unknown medical dimensions remain unknown; the order is not a patient-triage rating.

The first 20 canonical topics have bilingual candidates. Five have passed source cross-checking and independent adversarial editorial review; the other 15 remain outside qualified coverage while specific evidence gaps are resolved. Six of the original ten urgent-condition gaps still lack independently verified articles. This editorial status is separate from clinician approval. See the [OSA review](reports/batch-01-osa-independent.json), [torsion review](reports/batch-01-torsion-recheck.json) and [current batch validation and release record](reports/batch-01-pe-retinal-release-validation.json); that record, rather than these repository totals, determines the public deployment state.

Newly confirmed leaf mappings are myocardial infarction BA41.0/BA41.1/BA41.Z, pulmonary embolism BB00.0, and retinal detachment 9B73.0/9B73.3. The [MI scope review](reports/batch-01-mi-icd-scope-review.json) and [PE/retinal scope review](reports/batch-01-pe-retinal-icd-scope-review.json) record the remaining categories and concrete gaps; a shared article does not automatically cover a parent or every descendant.

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
