# Tests

This directory contains the test suite for geoip-geocode.

## Structure

- `test_*.py` - Test modules for each component
- `fixtures/` - Test fixtures and sample data

## Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=geoip_geocode --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_models.py
```

## Writing Tests

- Follow pytest conventions
- Use fixtures for reusable test data
- Mock external dependencies (databases, network calls)
- Aim for high test coverage

## Test Categories

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Provider tests**: Test provider implementations
