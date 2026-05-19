# LangChain Migration Plan (Marker)

## Goal
Standardize AI integrations in Marker and improve reliability by introducing:
- a shared LLM adapter,
- retry and model fallback handling,
- a unified flow for AI reports and website autofill.

## Implementation Status
- [x] Stage 1: Shared LLM invocation layer
- [x] Stage 2: Migrate AI report SQL generation to the shared layer
- [x] Stage 2: Migrate website autofill to the shared layer
- [x] Stage 2: Update Python dependencies
- [x] Stage 2: Update unit tests
- [x] Stage 3: Structured output (Pydantic) for company/project/contact/tag flows
- [x] Stage 3: Telemetry logging (latency, retries, token usage metadata)
- [x] Stage 3: Error dashboard and endpoint-level aggregated metrics
- [ ] Stage 4: Semantic search / RAG with langchain-community

## Delivered Scope
1. Shared AI adapter added: marker/utils/langchain_ai.py
- invoke_text(prompt, model, fallback_model, retries)
- invoke_json(prompt, model, fallback_model, retries)
- exponential backoff retry strategy
- model fallback support
- telemetry logs (success/retry/failure, elapsed time, usage metadata)

2. AI reports migrated to the adapter
- marker/utils/llm_report.py now uses invoke_text
- SQL validation and code-fence cleanup are preserved

3. Website autofill migrated to the adapter
- marker/utils/website_autofill.py now uses invoke_json
- page content size cap added before sending to the model
- structured output validation added via Pydantic models (company/project/contact)
- normalization and deduplication added for tag lists

4. Dependencies updated
- added: langchain, langchain-community, langchain-google-genai
- removed direct runtime dependency on google-genai SDK usage in app code paths

5. Configuration support added
- model selection via gemini.model
- fallback model via gemini.fallback_model
- retries via gemini.retries

6. Tests updated
- llm_report tests adapted to patch invoke_text
- website_autofill _gemini_json test adapted to patch invoke_json
- structured output tests added for autofill edge cases

7. AI telemetry dashboard added
- report route and view for aggregated AI metrics per source
- report list entry available from the Reports page

## Configuration
Required environment variable:
- GEMINI_API_KEY

Optional environment variables (backward-compatible fallback):
- GEMINI_FALLBACK_MODEL
- GEMINI_RETRIES

Primary application settings (preferred):
- gemini.model
- gemini.fallback_model
- gemini.retries

## Remaining Work
1. Observability completion
- build an error dashboard with per-endpoint aggregates (error rate, latency percentiles, retries)
- expose operational metrics suitable for monitoring/alerting

2. Premium AI features
- semantic search across companies/projects/comments
- RAG over internal notes and extracted website content
