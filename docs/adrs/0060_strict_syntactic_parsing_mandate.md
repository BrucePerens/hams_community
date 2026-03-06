# ADR 0060: Strict Syntactic Parsing Mandate

## Status
Accepted

## Context
Previously, the codebase utilized regular expressions (`re`) to extract CSRF tokens in tests, parse XML tags in the CI/CD linter, scrape HTML descriptions, and attempt to evaluate code strings. Regular expressions are mathematically and fundamentally incapable of robustly parsing context-free languages, nested data structures, or complex syntaxes. Minor variations in formatting, attribute ordering, whitespace, or nested blocks instantly break regex patterns, leading to brittle tests, false-positive linter failures, and unreliable scrapers.

## Decision
We explicitly ban the use of regular expressions for extracting, evaluating, or parsing **any sort of file or structured data whatsoever** when an actual syntactic parser is available.

* **XML/HTML:** MUST use `lxml.etree`, `lxml.html`, or `BeautifulSoup` to parse documents into an Abstract Syntax Tree (AST) before evaluation or querying via XPath.
* **Python/Source Code:** MUST use the native `ast` module to evaluate execution logic and structure.
* **Data Serialization:** MUST use native or standard parsers (e.g., `json`, `yaml`, `csv`) instead of regex to locate keys or extract values.
* **Regex Confinement:** The `re` module is strictly confined to evaluating flat, unstructured text, simple log lines, or highly constrained, simple alphanumeric formats (e.g., Maidenhead Grid Squares or Callsigns).
