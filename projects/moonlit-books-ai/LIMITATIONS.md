# Scope and limitations

Moonlit Books is an independent portfolio demonstration with real Open Library metadata and simulated shop data. It is not a commercial bookstore, an accounting product, or evidence of completed client work.

## Assistant

- Retrieval is BM25 lexical ranking over a small cached Open Library catalog and simulated handbook. It does not understand every paraphrase, language, preference, negation, or budget expression.
- Recommendation retrieval filters sample stock and simple numeric budget phrases. It does not enforce all semantic preferences. Models can still recommend an unsuitable retrieved title.
- Output checks reject unknown source IDs, unknown recommended IDs, excessive recommendations, and missing recommendation citations. They do not prove that each sentence is entailed by evidence.
- The prompt requests abstention and refusal to invent missing facts. These requests are not formal guarantees against hallucinations or prompt injection.
- Stock and prices are static samples. No stock is reserved and no transaction occurs.

## Invoices

- Only ten bundled, text-based synthetic PDFs are supported. No OCR, scans, multilingual documents, arbitrary uploads, or production document variability are evaluated.
- Amounts are compared with Decimal arithmetic at cent precision. Extraction can still misread a printed amount or identifier.
- The suspicious-instruction detector is a narrow pattern check. It is not a comprehensive document security system.
- A rule pass still requires human review. Review outcomes are local log entries; no payment, ledger posting, or external workflow is performed.
- Duplicate detection uses a fixed sample ledger. Review actions do not update that ledger.

## Evaluation

- 18 public cases: 8 assistant and 10 invoice cases. They are not statistically representative or held out from development.
- Passing a case means its programmed checks passed. It does not mean every sentence was factually verified.
- Some answer checks look for expected words; they do not assess all possible contradictory or misleading prose.
- Invoice accuracy counts six scalar fields plus one ordered line-item group per invoice. It is not per-character accuracy or production document accuracy.
- Failed model requests are included as failures; their elapsed time is not included in completed-call latency.
- Reported timing depends on hardware, model state, context length, load, and runtime version. It includes prompt processing and generation, and may include model warm-up.

## Deployment

This single-user local server has no authentication, TLS, rate limiting, or production queue. Do not expose it beyond loopback. Browser actions accept only local origins; that does not make the server a multi-user secure deployment. Treat the local environment as trusted. Use only synthetic inputs in the portfolio version.

## Open Library metadata

Titles, authors, first publication years and subjects are imported from source responses. Editorial reading tags and shelf genres are separate curation; prices and inventory are simulated. Metadata is work-level and may contain omissions or errors. The assistant has no full book text and must not claim passage-level knowledge. Source links are constructed only from validated Open Library work IDs. Original cover-style illustrations are labeled demo art.

API responses are cached for reproducibility; inference uses this local snapshot and does not search the entire Open Library catalog. A book absent from the snapshot is not necessarily absent from Open Library. The snapshot is refreshed explicitly, not on every question. Historical scores and screenshots under `results/archive/synthetic-catalog` use different data and do not validate the real-book version.

## Title lookup recognition

Explicit named/quoted and selected stock-question formats have a deterministic cached-catalog handoff rule. This is a workflow control, not proof that the model independently recognizes every missing title. Other natural-language phrasings, misspellings, translations and ambiguous titles can still be mishandled. Zero stock and absence from the cached catalog are different states; neither establishes whether Open Library or another shop has the book. The raw model handoff flag and application enforcement are distinguishable in the saved evaluation.
