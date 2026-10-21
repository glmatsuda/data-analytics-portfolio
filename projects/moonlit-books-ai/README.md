> **Public showcase:** [Explore the guided replay](https://glmatsuda.github.io/data-science-portfolio/moonlit-books/) · [Watch the 64-second captioned walkthrough](showcase/media/moonlit-books-walkthrough.mp4). The showcase replays measured outputs; the Python app below performs live local inference.

# Moonlit Books · Open Library AI Studio

A fictional independent bookstore using **real Open Library book metadata**. It demonstrates a source-grounded concierge, supplier invoice extraction with human review, and an AI evaluation dashboard. Independent portfolio work for Gian-Luca Matsuda; no client work is claimed.

**Real:** titles, author names, first publication years and subject labels returned by Open Library. **Editorial:** the portfolio's shelf genres and reading tags. **Simulated:** USD shop prices, stock, suppliers, invoices, policies, events and review actions. Original cover-style artwork is a demo design, not publisher cover art. No book text or publisher description is downloaded, and the assistant does not claim to have read the books.

## Run

Requires Python 3.10+ and [Ollama](https://ollama.com/download).

```sh
ollama serve
# In a second Terminal tab:
ollama pull qwen3:8b
```

If Ollama already serves the API, use that running instance. On macOS without a PATH shortcut, replace `ollama` with `/Applications/Ollama.app/Contents/Resources/ollama`.

```sh
python3 -m pip install -r requirements.txt
python3 app.py
```

Open **http://127.0.0.1:8867**. Keep the server Terminal running; stop with Control+C. `Start Moonlit Books.command` is a convenience launcher for the original Mac.

On the first launch, the importer performs three bounded, cached Open Library Search API requests for a curated list of 24 lookup targets. It validates title/author matches and work identifiers, including two explicitly reviewed original-title aliases for Frankenstein and the Sherlock Holmes story collection. Among matching records it prefers the one with the most editions; this is a selection heuristic, not a guarantee of bibliographic correctness. Unmatched optional targets are omitted and disclosed; an incomplete essential catalog fails explicitly rather than fabricating metadata. Subsequent launches reuse the saved catalog without network access. Only book lookup terms are sent to Open Library; concierge questions and invoice text stay local.

To refresh manually, stop the app, run `python3 import_openlibrary.py --refresh`, then restart. This deliberately small educational lookup is not a bulk data harvester or commercial API backend. Requests are spaced below one per second. See [Open Library API guidance](https://openlibrary.org/developers/api).

`pypdf` enables direct PDF text extraction. Without it, the interface explicitly identifies its bundled text-transcript fallback. This demo does not perform OCR or accept arbitrary uploads.

## Three connected workflows

1. **Book concierge:** BM25 lexical retrieval over cached real catalog records and eight simulated handbook entries. Qwen3 generates structured answers constrained to retrieved IDs; independent checks validate catalog IDs and source citations. Expand evidence and follow each Open Library work link.
2. **Invoice desk:** ten selectable synthetic PDFs, structured local extraction, precise Decimal reconciliation, vendor/catalog/duplicate/currency/quantity rules and a suspicious-instruction pattern check. A local human review log cannot trigger payment or accounting entries.
3. **Quality lab:** 18 actual model calls—eight assistant cases and ten invoice cases. Responses, failures, token counts and latency remain inspectable. The UI never substitutes prewritten AI answers or invented scores.

## Data provenance

| File | Meaning |
| --- | --- |
| `data/catalog.csv` | Real API fields, source links, editorial labels and simulated commercial fields |
| `data/catalog-info.json` | Source request URLs, timestamps, omitted targets and catalog SHA-256 |
| `data/openlibrary/*.json` | Cached, timestamped original API responses |
| `data/handbook.json` | Eight simulated shop policy records |
| `data/invoices/` | Ten synthetic PDF invoices and exact text transcripts |
| `data/invoice_truth.json` | Public expected extraction and exception fixtures |
| `data/evaluation_cases.json` | Public assistant regression cases |

The catalog is work-level metadata, not a promise about a specific edition or ISBN. API publication years and subject labels can be incomplete or inaccurate. Simulated prices do not correspond to market prices or an edition. Book links lead to source records, not claims that the books are freely downloadable.

## Architecture

```text
Open Library → bounded cached import → validated metadata + source provenance
Question → local BM25 retrieval → Qwen3 JSON → ID/citation contract → answer + sources
Synthetic invoice PDF → text extraction → Qwen3 JSON → rule checks → local human review
Public cases → same real inference functions → measured checks and saved report
```

There is no vector embedding pipeline, model training, live inventory, payment or accounting integration. Expected fixture values are used only for scoring, never as model inputs.

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 evaluate.py
```

Alternatively choose **Quality lab → Run live evaluation**. The latest completed result is saved to `results/evaluation.json`. Reports include the catalog fingerprint; the app will not display a saved report from a different catalog. Failed requests count as failed cases. Invoice accuracy measures six scalar fields and one ordered line-item group per invoice—70 groups total. Median latency covers completed model calls, including rejected responses when usage is available, and can include warm-up. It is not a performance guarantee.

Unit-test mocks exercise rejection paths only and never populate benchmark results. These public cases are a small regression suite, not held-out evidence of general accuracy. Citation membership does not prove sentence-level correctness. Read [LIMITATIONS.md](LIMITATIONS.md).

### Historical synthetic version

`results/archive/synthetic-catalog/` preserves the prior fictional catalog, tests, screenshots and results for reproducibility. That version improved from 15/18 to 17/18 passing cases after constraining the two ID namespaces separately. Those historical scores **do not apply to the Open Library catalog**. Its baseline token counts excluded rejected requests; later runs retain usage for completed responses rejected by contract checks. New catalog results must be measured separately.

## Licensing and privacy

Original code, editorial labels and simulated shop data are MIT licensed. Open Library metadata is attributed separately; its [licensing statement](https://openlibrary.org/developers/licensing) says the Internet Archive asserts no new proprietary rights while noting that existing rights may apply. This project does not relicense third-party material under MIT. No publisher cover images or book text are included.

Ollama and model weights are separate dependencies. [Qwen3 8B](https://ollama.com/library/qwen3:8b) is distributed under Apache 2.0; model weights are excluded from this repository. The app binds to loopback and uses local inference at `127.0.0.1:11434`. It is a trusted, single-user demo with no authentication or production deployment controls. Ordinary concierge conversations are not saved by the app; benchmark responses and explicit review decisions are stored locally. Ollama has its own runtime logs and configuration.

## Open Library run before the handoff fix

The corrected catalog imported all **24/24 lookup targets**. All **17 code/provenance tests** passed. The real Qwen3 run passed **17/18 cases**, with **70/70 invoice field groups** correct. `missing-title` failed because the assistant did not set the expected human-handoff flag for an absent title. Its actual response and checks remain in `results/evaluation.json`; this was the failure addressed by the handoff rule described below, and was not hidden or excluded. The earlier Open Library matching run is preserved separately under `results/archive/openlibrary-initial-matches`. The latest report fingerprint matches the current catalog.

## Missing-title handoff rule

The `openlibrary-title-handoff-v3` pipeline adds an application-owned title check before generation. It recognizes explicit `book called/titled/named` requests, double/curly quoted title lookups, and `Do you have/stock/carry/find [title] in stock/available` questions. It compares normalized titles against the entire cached catalog, with reviewed subtitle/collection-note variants. It does not fuzzily claim a different book is in stock. Known records with zero inventory remain present records, rather than being mislabeled missing. General genre and policy questions stay on normal retrieval. Other phrasings still rely on retrieval and model behavior.

For a recognized absent title, the model receives the verified local lookup and relevant shop policy evidence. Its output schema requires human review and no unrelated recommendations. After generation, the application independently enforces `needs_human=true`, even if a provider ignores the schema. The report retains `model_needs_human`, `catalog_lookup` and `handoff_rule_applied`, so a passing workflow check is not confused with an unassisted model capability. A visible notice says the title is absent only from the cached snapshot; no claim is made about the whole Open Library. Human review means an on-screen handoff flag, not an automatically sent message.

The prior failing Open Library report is retained under `results/archive/openlibrary-before-handoff-fix`. Reports are now tied to both catalog hash and pipeline version; stale scores are hidden until the new version is evaluated.

## Latest handoff-fix result

The v3 pipeline passed **18/18 live workflow cases**, with **70/70 invoice field groups** correct, plus **28 deterministic code/provenance checks**. The browser missing-title shortcut also showed the cached-catalog scope and human-confirmation notice. This pass reflects the combined model-plus-application workflow. It does not establish perfect model accuracy or recognition of every possible phrasing. The actual responses, raw model flags, applied rules, timing and pipeline version are saved in the current evaluation report.
