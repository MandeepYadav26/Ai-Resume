# Changelog

All notable changes to the AI Resume Analyzer project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [1.0.0] - 2026-08-12

### Added
- Initial release of Flask web application for resume screening and ATS analysis.
- PDF text extraction supporting PyPDF2 and pypdf fallback mechanisms.
- TF-IDF Cosine Similarity calculation between job description and resume content.
- Contact details extraction for email addresses, phone numbers, and candidate names.
- CSV report generator exporting candidate metrics to `matched_candidates.csv`.
- Comprehensive `README.md` project documentation and `.gitignore` file.

### Automation & Testing
- Automated unit test suite in `test_resume_analyzer.py` covering core NLP and scoring functions.
- GitHub Actions CI workflow in `.github/workflows/ci.yml` for automated testing.
- MIT License file added to repository.

### Governance & Documentation
- Community contribution guidelines in `CONTRIBUTING.md`.
- Pull Request template in `.github/PULL_REQUEST_TEMPLATE.md`.
- Issue templates for bug reports and feature requests under `.github/ISSUE_TEMPLATE/`.
- Security policy in `SECURITY.md`.
- Code of Conduct in `.github/CODE_OF_CONDUCT.md`.
