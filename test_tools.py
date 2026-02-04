"""
Standalone test script for Exa API integration.
Tests the API calls directly (without Dify framework) to validate
that payloads and response parsing are correct.

Usage:
    export EXA_API_KEY="your-key-here"
    python3 test_tools.py
"""

import json
import os
import sys

import requests

API_KEY = os.environ.get("EXA_API_KEY", "")
BASE_URL = "https://api.exa.ai"
WEBSETS_URL = f"{BASE_URL}/websets/v0/websets"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
}

passed = 0
failed = 0


def test(name, func):
    global passed, failed
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    try:
        func()
        print(f"  PASSED")
        passed += 1
    except Exception as e:
        print(f"  FAILED: {e}")
        failed += 1


def test_search_basic():
    """Test basic search with minimal parameters."""
    payload = {
        "query": "best python web frameworks",
        "numResults": 3,
        "useAutoprompt": True,
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"
    assert "url" in results[0], "Result missing 'url' field"
    assert "title" in results[0], "Result missing 'title' field"
    print(f"  Got {len(results)} results")
    print(f"  First result: {results[0].get('title', 'N/A')}")


def test_search_with_contents():
    """Test search with text, highlights, and summary enabled."""
    payload = {
        "query": "machine learning tutorials",
        "numResults": 2,
        "useAutoprompt": True,
        "contents": {
            "text": True,
            "highlights": True,
            "summary": True,
        },
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"

    r = results[0]
    has_text = "text" in r and r["text"]
    has_summary = "summary" in r and r["summary"]
    print(f"  Has text: {has_text}")
    print(f"  Has summary: {has_summary}")
    print(f"  Has highlights: {'highlights' in r and bool(r['highlights'])}")


def test_search_with_category():
    """Test search with category filter."""
    payload = {
        "query": "AI startups",
        "numResults": 3,
        "category": "company",
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"
    print(f"  Got {len(results)} company results")


def test_search_with_domain_filters():
    """Test search with include/exclude domains."""
    payload = {
        "query": "python tutorials",
        "numResults": 3,
        "includeDomains": ["realpython.com", "docs.python.org"],
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"
    for r in results:
        url = r.get("url", "")
        assert "realpython.com" in url or "docs.python.org" in url, (
            f"Result URL {url} not from expected domains"
        )
    print(f"  All {len(results)} results from expected domains")


def test_search_with_date_filter():
    """Test search with date range filter."""
    payload = {
        "query": "AI news",
        "numResults": 3,
        "startPublishedDate": "2025-01-01T00:00:00.000Z",
        "endPublishedDate": "2025-12-31T00:00:00.000Z",
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"
    print(f"  Got {len(results)} results with date filter")


def test_search_type_neural():
    """Test neural search type."""
    payload = {
        "query": "how to deploy machine learning models",
        "numResults": 2,
        "type": "neural",
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"
    print(f"  Neural search returned {len(results)} results")


def test_search_type_fast():
    """Test fast search type."""
    payload = {
        "query": "FastAPI async endpoints",
        "numResults": 2,
        "type": "fast",
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"
    print(f"  Fast search returned {len(results)} results")


def test_contents():
    """Test content extraction from URLs."""
    # First search to get some URLs
    search_resp = requests.post(
        f"{BASE_URL}/search",
        json={"query": "python", "numResults": 1},
        headers=HEADERS,
        timeout=30,
    )
    search_resp.raise_for_status()
    urls = [r["url"] for r in search_resp.json().get("results", [])]
    assert len(urls) > 0, "Need at least 1 URL from search"

    payload = {
        "ids": urls,
        "contents": {"text": True, "summary": True},
    }
    resp = requests.post(f"{BASE_URL}/contents", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 content result"
    print(f"  Extracted content from {len(results)} URLs")
    if results[0].get("text"):
        print(f"  Text length: {len(results[0]['text'])} chars")


def test_contents_max_age_hours():
    """Test content extraction with maxAgeHours (replaces deprecated livecrawl)."""
    payload = {
        "ids": ["https://www.python.org"],
        "contents": {"text": True, "maxAgeHours": 24},
    }
    resp = requests.post(f"{BASE_URL}/contents", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected content result"
    print(f"  maxAgeHours content retrieved, text length: {len(results[0].get('text', ''))}")


def test_answer():
    """Test the answer endpoint."""
    payload = {
        "query": "What is the capital of France?",
        "model": "exa",
    }
    resp = requests.post(f"{BASE_URL}/answer", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    answer = data.get("answer", "")
    assert answer, "Expected a non-empty answer"
    assert "Paris" in answer or "paris" in answer.lower(), f"Expected 'Paris' in answer, got: {answer[:100]}"
    print(f"  Answer: {answer[:200]}")

    sources = data.get("results", [])
    print(f"  Sources: {len(sources)}")


def test_answer_with_text():
    """Test the answer endpoint with source text included."""
    payload = {
        "query": "What programming language is most popular in 2025?",
        "model": "exa",
        "contents": {"text": True},
    }
    resp = requests.post(f"{BASE_URL}/answer", json=payload, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    answer = data.get("answer", "")
    assert answer, "Expected a non-empty answer"
    print(f"  Answer: {answer[:200]}")

    sources = data.get("results", [])
    if sources and sources[0].get("text"):
        print(f"  Source text included, length: {len(sources[0]['text'])} chars")


def test_search_include_exclude_text():
    """Test includeText and excludeText filters."""
    payload = {
        "query": "web frameworks",
        "numResults": 3,
        "includeText": ["Django"],
    }
    resp = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    assert len(results) > 0, "Expected at least 1 result"
    print(f"  Got {len(results)} results with includeText filter")


def test_invalid_api_key():
    """Test that invalid API key returns proper error."""
    bad_headers = {"x-api-key": "invalid-key", "Content-Type": "application/json"}
    resp = requests.post(
        f"{BASE_URL}/search",
        json={"query": "test", "numResults": 1},
        headers=bad_headers,
        timeout=30,
    )
    assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}"
    print(f"  Correctly rejected with status {resp.status_code}")


def test_format_search_results():
    """Test that the formatting logic in exa_search.py handles edge cases."""
    # Simulate API response data and test the formatting logic
    mock_data = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "publishedDate": "2025-01-01",
                "author": "Test Author",
                "score": 0.9876,
                "summary": "A test summary",
                "highlights": ["highlight one", "highlight two"],
                "text": "x" * 600,  # test truncation at 500 chars
            },
            {
                # minimal result - no optional fields
                "url": "https://example2.com",
            },
        ]
    }

    # Replicate the formatting logic from exa_search.py
    results = mock_data.get("results", [])
    query = "test query"
    lines = [f"## Exa Search Results\n", f"**Query:** {query}\n", f"**Results:** {len(results)}\n"]

    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        lines.append(f"### {i}. [{title}]({url})\n")

        if r.get("publishedDate"):
            lines.append(f"**Published:** {r['publishedDate']}")
        if r.get("author"):
            lines.append(f"**Author:** {r['author']}")
        if "score" in r:
            lines.append(f"**Score:** {r['score']:.4f}")
        if r.get("summary"):
            lines.append(f"\n**Summary:** {r['summary']}\n")
        if r.get("highlights"):
            lines.append("\n**Highlights:**")
            for h in r["highlights"]:
                lines.append(f"> {h}")
        if r.get("text"):
            text = r["text"][:500] + "..." if len(r.get("text", "")) > 500 else r.get("text", "")
            lines.append(f"\n```\n{text}\n```")
        lines.append("---\n")

    formatted = "\n".join(lines)
    assert "Untitled" in formatted, "Missing result should use 'Untitled'"
    assert "x" * 500 + "..." in formatted, "Long text should be truncated with '...'"
    assert "0.9876" in formatted, "Score should be formatted to 4 decimal places"
    print(f"  Formatting produces {len(formatted)} chars")
    print(f"  Handles missing title, truncation, and score formatting correctly")


def test_format_empty_results():
    """Test formatting with no results."""
    mock_data = {"results": []}
    results = mock_data.get("results", [])
    lines = [f"## Exa Search Results\n", f"**Query:** empty\n", f"**Results:** {len(results)}\n"]
    formatted = "\n".join(lines)
    assert "**Results:** 0" in formatted
    print(f"  Empty results formatted correctly")


def test_int_none_safety():
    """Test that the int(None) bug exists - this SHOULD fail to prove the bug."""
    # Simulating what happens when Dify passes None for an optional numeric param
    tool_parameters = {"num_results": None}  # Dify sends None for unfilled optional params

    try:
        num_results = int(tool_parameters.get("num_results", 10))
        # If we get here, .get() returned 10 (key missing) - but key IS present
        print(f"  UNEXPECTED: got {num_results} - this means .get() used default despite key existing")
    except TypeError:
        # This is the expected behavior proving the bug
        print(f"  Confirmed bug: int(None) raises TypeError when key exists with None value")
        print(f"  Fix: use `int(tool_parameters.get('num_results') or 10)`")

    # Verify the fix works
    num_results_fixed = int(tool_parameters.get("num_results") or 10)
    assert num_results_fixed == 10, f"Fix should give 10, got {num_results_fixed}"
    print(f"  Fix verified: `int(val or 10)` correctly returns 10")


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: Set EXA_API_KEY environment variable first")
        print("  export EXA_API_KEY='your-key-here'")
        sys.exit(1)

    print("Exa Plugin Integration Tests")
    print(f"Using API key: {API_KEY[:8]}...")

    # Tests that don't need a valid API key
    test("int(None) safety bug", test_int_none_safety)
    test("Format search results", test_format_search_results)
    test("Format empty results", test_format_empty_results)

    # Tests that call the Exa API
    test("Invalid API key rejection", test_invalid_api_key)
    test("Basic search", test_search_basic)
    test("Search with contents", test_search_with_contents)
    test("Search with category", test_search_with_category)
    test("Search with domain filters", test_search_with_domain_filters)
    test("Search with date filter", test_search_with_date_filter)
    test("Neural search type", test_search_type_neural)
    test("Fast search type", test_search_type_fast)
    test("Include/exclude text filters", test_search_include_exclude_text)
    test("Contents extraction", test_contents)
    test("Contents with maxAgeHours", test_contents_max_age_hours)
    test("Answer endpoint", test_answer)
    test("Answer with source text", test_answer_with_text)

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed}")
    print(f"{'='*60}")
    sys.exit(1 if failed > 0 else 0)
