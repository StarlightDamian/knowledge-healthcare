# Changelog

## Research maps with shared content — 2026-09-29

Added bilingual cancer and life-course collections from the two supplied research reports. The cancer map contains 34 statistical groups and two supplementary groups. The life-course map contains 20 canonical health factors in eight groups, referenced by six disjoint age bands and a pregnancy context. Existing condition articles and shared factors are linked by ID; stage, histology and molecular markers remain separate classification axes. New map units are counted separately from condition and ICD coverage.

Added local map search, group/stage filters, section navigation, source locators and links to existing condition details. Collection queries and reading state survive language changes. Sources were checked against official patient information and original studies; import records retain statistical versions and evidence boundaries. The build remains one offline HTML file, with no new production dependency. Existing condition data, CSV columns and review states are preserved.

## Reading copy and coverage review — 2026-09-29

Reviewed all 72 bilingual topics using Anti-Defensive Writing. Replaced redundant self-limitations with direct explanations while retaining medical conditions, numerical thresholds, emergency actions and evidence limits. Removed repeated review badges and chapter notices; actual review facts now appear in the content/source explanation and expandable topic source information. Updated all 12 interface languages and the 72 / 32 / 2 homepage metrics.

Saved the failed 95% coverage review, the unmeasured rate and ten known urgent gaps. The full ICD-11 denominator and mappings remain the first roadmap step. No new condition bodies were added. Review states, source links, CSV columns and clinical gates are preserved.

## Local content and reading update — 2026-09-29

Expanded the existing 72 bilingual drafts into introductions and knowledge lists, retaining all 14 field IDs, draft states and content-bound review hashes. Added per-section editorial source records and a reproducible content audit. These records do not create medical sign-off.

Matched the fitness reference palette and spacing; added two-level department navigation, a mobile drawer, language-state preservation, a detail contents index and full comparison-cell expansion. CSV keeps the complete text and line breaks. The 95% target now explicitly uses ICD-11 MMS 2026-01 independent condition categories; the denominator and mappings remain pending, with a phased gap plan. No commit, push or deployment is part of this update.

Current HTTP, offline-file and responsive verification evidence supersedes the original environment-limited report below; see `reports/test-results.json`.

## 0.1.0-preview — 2026-09-29

First working preview: 72 bilingual drafts, 18 domains, 154 source records, 198 separate backlog titles, 12 UI locales with explicit fallback, local lexical/BM25 search, danger-phrase draft rules, full-topic comparison and CSV, self-contained HTML, structural/clinical gates, integrity packaging and regression tests.

Fixed an unsafe sentence-splitting regression that broke the phrase “喘不过气”. Corrected obsolete source paths and a wrongly matched encyclopedia URL during source inspection. Preserved the NHS PMOS / other-source PCOS naming difference rather than silently forcing one label.

No clinician approvals, no independent clinical validation, no measured 95% need coverage, no full medical localization beyond bilingual drafts. Browser interaction was exercised using in-memory HTML because the build environment blocked navigation; remote GitHub deployment has not been tested or performed here.
