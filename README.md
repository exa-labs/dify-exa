# Exa Plugin for Dify

A [Dify](https://dify.ai) plugin that integrates [Exa's](https://exa.ai) AI-powered search API. Use it in Dify agents and workflows to search the web, extract page contents, get AI-generated answers, and build structured datasets with Websets.

## Tools

### Exa Search
Search the web with multiple modes and category filters.

- **Search types**: `auto` (recommended), `neural`, `fast`, `deep`
- **Categories**: company, people, news, research paper, tweet, personal site, financial report
- **Filters**: domain include/exclude, date range (ISO 8601), text include/exclude
- **Content options**: text extraction, highlights, summaries, cache control via `maxAgeHours`

### Exa Contents
Extract text, highlights, and summaries from specific URLs.

- Cache control via `maxAgeHours` (0 = always livecrawl, -1 = cached only)
- Subpage crawling
- AI-generated page summaries

### Exa Answer
Ask a question and get an AI-generated answer with cited web sources.

- Models: `exa` (standard) and `exa-pro` (higher quality)
- Optionally include full source text

### Exa Create Webset
Create a Webset to find, verify, and enrich web entities at scale.

- **Entity types**: company, person, article, research paper
- **Criteria**: up to 5 evaluation criteria to filter results
- **Enrichments**: extract structured data (CEO name, funding, website, etc.) from each result
- Async processing — results are available once the Webset finishes

### Exa Get Webset
Check the status of a Webset and retrieve its items.

- View processing progress (% complete, items found/analyzed)
- Optionally include items with enrichment data

### Exa List Webset Items
List all items from a Webset with pagination.

- Paginate through large result sets (up to 100 items per page)
- Includes enrichment data for each item

## Setup

1. Get an API key from the [Exa Dashboard](https://dashboard.exa.ai/api-keys) (includes $10 free credit)
2. Install this plugin in your Dify instance
3. Enter your API key in the plugin credentials

## Development

```bash
# Clone the repo
git clone https://github.com/exa-labs/dify-exa.git
cd dify-exa

# Copy env template and configure for your Dify debug instance
cp .env.example .env

# Run in debug mode
python -m main
```

## Packaging

```bash
dify plugin package ./dify-exa
```
