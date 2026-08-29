# RAG Coverage Research Report

Date: 2026-08-29

## Scope

Assess whether `00-MAP.md` and `03-Stage3-RAG.md` align, and whether `03-Stage3-RAG.md` contains the full set of production and industry-adopted topics needed for a complete RAG implementation.

Assumption: "Complete RAG" means a production-grade enterprise or government/internal assistant, not a demo. It includes ingestion, indexing, retrieval, authorization, generation, evaluation, operations contracts, security, lifecycle, and currently adopted market patterns.

## Short Answer

`00-MAP.md` and `03-Stage3-RAG.md` align. The map's Stage 3 index matches the Stage 3 file's explicit pipeline order: ingestion, chunking, embeddings, vector store, retrieval, security trimming, generation, lifecycle, caching, advanced RAG, and evaluation.

`03-Stage3-RAG.md` is very strong for core production RAG. It covers the most important build requirements: connectors, incremental sync, OCR/layout/table extraction, Arabic handling, chunking, embeddings, vector indexes, hybrid retrieval, reranking, ACL pre-filtering, grounded generation, citations, abstention, lifecycle/deletion, caching, advanced RAG patterns, and evaluation/golden sets.

It is not yet "200% market-complete" as a standalone RAG reference. It should add several explicit topics that are now mainstream in vendor products, vector databases, evaluation systems, and GenAI security guidance.

## Alignment Evidence

- `00-MAP.md` Stage 3 index lists `8.3.1` through `8.3.10`, plus `8.3.5.8` and `8.3.8.10`.
- `03-Stage3-RAG.md` states the order is pipeline order, not numeric order: security trimming sits immediately after retrieval, and lifecycle/caching come before advanced RAG/evaluation.
- The Stage 3 file contains matching topic sections for ingestion, Arabic handling, chunking, embeddings, vector stores, retrieval, security trimming, generation, lifecycle, caching, advanced RAG, evaluation, and golden-set construction.

## Strong Coverage Already Present

- Ingestion: connectors, delta/change feeds, timestamps, content hashes, deleted/moved documents, ACL capture.
- Document processing: PDFs, Office files, scans, OCR, layout, tables, figures, page/section/bounding-box metadata.
- Arabic: RTL, OCR, normalization, bilingual documents, token ratios, multilingual embeddings, Arabic golden-set cases.
- Chunking: recursive/layout-aware/semantic chunking, parent-child retrieval, metadata enrichment, migration risk.
- Embeddings: model choice, dimensions, normalization, multilingual choice, re-embedding, versioning, cost.
- Vector stores: Azure AI Search, pgvector, HNSW, IVFFlat, filterable metadata, hybrid index shape, refresh/deletion.
- Retrieval: hybrid search, RRF, reranking, query rewriting, expansion, HyDE, multi-query, metadata filters.
- Authorization: permission-aware retrieval, transitive principals, pre-filtering, cache key safety, parent expansion re-check.
- Generation: grounded prompts, citations, abstention, quote verification, answer schemas, source links.
- Lifecycle: deletion propagation, permission-change propagation, right-to-erasure, blue/green re-index.
- Caching: exact, embedding, rewritten-query, semantic cache, invalidation, permission-class keys.
- Advanced patterns: GraphRAG, agentic RAG, contextual retrieval, multi-hop, Table RAG, SQL/text-to-SQL.
- Evaluation: groundedness, faithfulness, answer relevance, context precision/recall, hit rate, RAGAS, CI gates, golden sets.

## Market-Completeness Gaps

1. RAG decision framework: add when not to use RAG, long-context vs RAG, managed knowledge base vs custom build, classic vs agentic retrieval, and source-of-truth decisions.

2. Managed RAG/KM market patterns: add explicit comparison of Azure AI Search/Foundry IQ, Amazon Bedrock Knowledge Bases, Google Agent Search/RAG APIs, Copilot/Graph connector style knowledge layers, and self-managed vector DB patterns.

3. Vector-store tenant architecture: separate this from ACL trimming. Cover collection-per-tenant vs namespace/payload filter/shard strategies, noisy-neighbor concerns, tenant-local indexes/statistics, and physical vs logical isolation.

4. Vector compression and quantization: scalar, binary, product/rotational/vendor-specific quantization, oversampling, rescoring, RAM/disk/cost/recall tradeoffs.

5. Modern retrieval representations: dense plus sparse neural retrieval, SPLADE/miniCOIL-style sparse vectors, named or multiple vectors per item, late-interaction/ColBERT-style retrieval or reranking, and multi-stage retrieval graphs.

6. Diversity, deduplication, and context packing: MMR/crowding/source balancing, near-duplicate collapse, max chunks per document/source, token-budget packing, and lost-in-the-middle ordering.

7. Public/fresh web grounding: web crawlers, robots.txt, include/exclude rules, crawl rate, Google Search grounding, custom search API grounding, public-web trust scoring, and mixing web results with internal documents.

8. Full multimodal RAG: image-to-text, image-to-image, chart/diagram retrieval, audio/video transcript plus scene indexing, multimodal embeddings, image citations, and multimodal prompt-injection risk.

9. Source trust and poisoning gates inside Stage 3: trusted source inventory, source authentication, hidden text detection, indexing approval workflows, provenance integrity, source conflict resolution, and poisoning audits.

10. Minimum RAG observability contract: query text, rewritten query, retrieved document IDs, scores, filters, corpus/index/retrieval policy versions, cache hits, token/cost, latency, and redaction policy.

11. Retrieval benchmarking expansion: add nDCG@k, Precision@k, Recall@k, MAP/MRR, graded relevance, confidence intervals, pairwise evaluation, and business outcome metrics.

12. Product/API integration patterns: retrieval as a tool, knowledge-base endpoints, Retrieve/RetrieveAndGenerate style APIs, streaming retrieval/generation, timeouts, fallbacks, and circuit breakers.

## Source Ledger

- Microsoft Azure AI Search RAG overview: RAG challenges include query understanding, multi-source data access, token constraints, latency, and security/governance; it distinguishes agentic retrieval from classic RAG and lists content preparation and relevance techniques. URL: https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview
- Microsoft Azure AI Search vector filters: vector filtering mode affects latency, recall, and false-negative risk; pre-filtering is important for security-sensitive filtering. URL: https://learn.microsoft.com/en-us/azure/search/vector-search-filters
- Microsoft Azure AI Search quantization: scalar and binary quantization reduce vector memory/disk footprint and use oversampling/rescoring to mitigate lossy compression. URL: https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-quantization
- AWS Prescriptive Guidance for Bedrock Knowledge Bases: managed RAG uses connectors, inclusion/exclusion filters, incremental sync, web crawler controls, and managed or third-party vector stores. URL: https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/rag-fully-managed-bedrock.html
- Google Cloud Agent Search/RAG APIs: custom RAG includes document layout parsing, text/multimodal embeddings, Vector Search, ranking APIs, and grounded generation with data stores or Google Search. URL: https://docs.cloud.google.com/generative-ai-app-builder/docs/builder-apis
- Qdrant hybrid queries and full-text search: market vector DBs support multi-stage queries, named vectors, dense+sparse fusion, RRF, BM25, SPLADE++, and miniCOIL-style sparse vectors. URLs: https://qdrant.tech/documentation/search/hybrid-queries/ and https://qdrant.tech/documentation/search/text-search/full-text-search/
- Qdrant multitenancy: tenant-aware storage/indexing can co-locate vectors for performance and isolation patterns. URL: https://qdrant.tech/documentation/manage-data/multitenancy/
- OWASP GenAI LLM08 Vector and Embedding Weaknesses: covers cross-context leaks, embedding inversion, data poisoning, permission-aware stores, source authentication, classification, and retrieval logging. URL: https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/
- OWASP GenAI LLM01 Prompt Injection: indirect prompt injection can happen through modified RAG repository documents; mitigations include filtering, least privilege, content segregation, and adversarial testing. URL: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- OpenTelemetry GenAI semantic conventions: retrieval documents, retrieval query text, system instructions, and tool data need trace fields and sensitive-data handling. URL: https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/
- Ragas metrics: RAG evaluation metrics include context precision, context recall, entities recall, noise sensitivity, response relevance, and faithfulness. URL: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- LangSmith RAG evaluation: RAG evaluation should cover correctness, relevance, groundedness, and retrieval relevance; offline and online evaluation are part of the lifecycle. URLs: https://docs.langchain.com/langsmith/evaluate-rag-tutorial and https://docs.langchain.com/langsmith/evaluation-concepts

## Recommendation

Treat `03-Stage3-RAG.md` as production-core complete, but not market-exhaustive. Add a short "Market-complete RAG extensions" section or add subtopics under existing sections. Most gaps are additive; they do not require rewriting the current structure.
