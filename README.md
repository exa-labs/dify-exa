# Exa Plugin for Dify

A [Dify](https://dify.ai) plugin that integrates [Exa's](https://exa.ai) AI-powered search API. Use it in Dify agents and workflows to search the web, extract page contents, and get AI-generated answers with cited sources.

## Tools

### Exa Search
Search the web with multiple modes and category filters.

- **Search types**: `auto`, `neural`, `keyword`, `fast`, `deep`
- **Categories**: company, people, news, research paper, PDF, GitHub, tweet, personal site, LinkedIn profile, financial report
- **Filters**: domain include/exclude, date range, text include/exclude
- **Content options**: text extraction, highlights, summaries, live crawl

### Exa Contents
Extract text, highlights, and summaries from specific URLs.

- Supports live crawling for fresh content
- Subpage crawling
- AI-generated page summaries

### Exa Answer
Ask a question and get an AI-generated answer with cited web sources.

- Models: `exa` (standard) and `exa-pro` (higher quality)
- Optionally include full source text

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
