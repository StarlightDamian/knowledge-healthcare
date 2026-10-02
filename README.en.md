# Open Medical Guide

**0.2.0-online — an online health knowledge library with local search, department navigation and comparison.**

**Live site: [https://www.zengyuwei.cn/healthcare/](https://www.zengyuwei.cn/healthcare/)**

[GitHub repository](https://github.com/StarlightDamian/knowledge-healthcare) · [Personal homepage](https://www.zengyuwei.cn/home/)

[中文](README.md) · [Open the built page](index.html) · [Architecture](docs/architecture.md)

The current repository includes 82 Chinese/English health topics, 14 content dimensions, introductions and knowledge lists, local lexical/BM25 retrieval, and danger-phrase alerts. Navigation has exactly two levels: 11 department groups and 33 populated specialties. Details prioritize danger signs and provide a chapter index. Comparison cells expand to full text; CSV retains all text and line breaks. The top-right language selector preserves filters, search, selection and open details. There are 12 UI locales with explicit English medical-text fallback for 10 of them.

Two additional collections organize the supplied research reports: a cancer map with 34 statistical groups plus two supplementary groups, and a life-course map with 20 shared factors in eight groups. Six disjoint age bands reference the same factors; pregnancy is an additional context. Cancer pages distinguish site, pathology, stage and biomarkers, with evidence and burden context. Links reuse existing condition articles, including breast and colorectal cancer. Each collection keeps its own search query, and department navigation returns to condition topics. See the [MECE mapping](docs/research-mece-map.md), [cancer import record](reports/research-cancer-import.md) and [life-course import record](reports/research-lifecycle-import.md).

Repository content and sources: 82 topics (77 conditions or health concerns and five symptom entries), 1,148 bilingual condition sections and 608 source records. The project-wide editorial scope contains 1,456 sections. Eleven articles have completed independent claim verification: 154 sections and 691 bilingual claims; zero articles have clinician sign-off. This P0 batch adds meningitis, sepsis, diabetic ketoacidosis, aortic dissection and postpartum hemorrhage, and expands the existing anaphylaxis article. [Batch and review records](reports/p0-batch-01.json) preserve claim-specific sources, conditions and review findings. The page provides section references and an expandable “Sources and editorial information” panel. Three trial cards contain abstract-level summaries; a fourth contains bibliographic metadata.

The frozen ICD-11 MMS 2026-01 denominator contains 13,155 eligible independent categories. Fully evidence-qualified coverage is 30 / 13,155 (approximately 0.228050%), leaving 13,125 unqualified. The final target is 100%; 95%, or 12,498 qualified categories, is an intermediate milestone. Mapping states are 30 confirmed, 32 partial and 46 pending. This measures evidence and category-scope completion, not the percentage of patients covered. The 189 title-only tasks and 56 map units remain separate. See the [coverage report](reports/icd-coverage.json), [roadmap](docs/coverage-audit-and-roadmap.md), [complete priority list](docs/icd-priorities/index.md) and [full CSV](reports/icd-priorities.csv). Priority is an editorial schedule, not patient triage; all unfinished P0 leaves remain in the queue.

Ten of the initial 20 canonical topics have passed source cross-checking and independent editorial review; ten retain explicit evidence or content gaps. This P0 batch adds five articles and expands existing anaphylaxis: 84 sections and 370 bilingual claims. Its 49 candidate categories were reviewed individually: 22 complete and 27 partial. Across the complete P0 inventory, 29 of 133 categories are complete and 104 remain pending. Nine of the original ten urgent-condition articles are now independently verified; carbon monoxide poisoning remains planned. See the [P0 category review](reports/p0-batch-01-icd-scope-review.json) and [validation and release record](reports/p0-batch-01-release-validation.json) for actual scope and public deployment status.

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
