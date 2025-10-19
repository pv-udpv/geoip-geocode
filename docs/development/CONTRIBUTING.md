# Contributing to geoip-geocode

Thank you for your interest in contributing to geoip-geocode! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/pv-udpv/geoip-geocode.git
cd geoip-geocode
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

4. Download GeoLite2 database for testing (optional):
   - Sign up at https://www.maxmind.com/en/geolite2/signup
   - Download GeoLite2-City.mmdb
   - Place in project root or specify path

## Code Standards

### Formatting and Linting

We use Black for formatting and Ruff for linting:

```bash
# Format code
black geoip_geocode tests

# Lint code
ruff check geoip_geocode tests

# Auto-fix linting issues
ruff check --fix geoip_geocode tests

# Type checking (optional)
mypy geoip_geocode
```

### Code Style

- Line length: 88 characters (Black default)
- Use type hints where practical
- Follow PEP 8 conventions
- Write docstrings for public APIs (Google style)
- Keep functions focused and small

### Documentation

- All public classes, functions, and modules need docstrings
- Include usage examples in docstrings
- Update README.md for user-facing changes
- Add comments for complex logic only

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=geoip_geocode --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_geodata_creation
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Test edge cases and error conditions
- Aim for high coverage of new code

Example test:
```python
def test_provider_lookup():
    """Test that provider lookup returns valid GeoData."""
    config = ProviderConfig(name="test", enabled=True)
    provider = TestProvider(config)
    
    result = provider.lookup("8.8.8.8")
    
    assert result is not None
    assert isinstance(result, GeoData)
    assert result.geoname_id > 0
```

## Adding a New Provider

To add support for a new geocoding provider:

1. Create a new file in `geoip_geocode/providers/`:
```python
# geoip_geocode/providers/newprovider.py
from typing import Optional
from geoip_geocode.registry import BaseProvider
from geoip_geocode.models import GeoData, ProviderConfig

class NewProvider(BaseProvider):
    """Description of the new provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # Initialize your provider
    
    def lookup(self, ip_address: str) -> Optional[GeoData]:
        """Look up geographic data for an IP address."""
        # Implement lookup logic
        # Must return GeoData with valid geoname_id
        pass
    
    def is_available(self) -> bool:
        """Check if provider is ready."""
        return self.config.enabled and self._ready
```

2. Add to `geoip_geocode/providers/__init__.py`:
```python
from geoip_geocode.providers.newprovider import NewProvider

__all__ = ["GeoIP2Provider", "NewProvider"]
```

3. Write tests in `tests/test_newprovider.py`

4. Update documentation:
   - Add example to README.md
   - Update IMPLEMENTATION.md
   - Add provider-specific configuration examples

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests and linting: `pytest && black . && ruff check .`
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### PR Guidelines

- Describe what your PR does
- Link to related issues
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass
- Keep PRs focused and small
- Follow commit message conventions

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for IPStack provider

- Implement IPStackProvider class
- Add configuration options
- Include tests and documentation
- Update examples
```

## Feature Requests and Bug Reports

### Reporting Bugs

When reporting bugs, please include:
- Python version
- Package version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces
- Minimal code example

### Requesting Features

For feature requests:
- Describe the use case
- Explain why it's useful
- Propose an implementation approach (if possible)
- Consider backwards compatibility

## Code Review

All contributions require code review. Reviewers will check:
- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations
- Backwards compatibility

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions:
- Check the documentation
- Look at existing issues
- Open a new issue for discussion

## Getting Help

- Read the README.md
- Check examples.py
- Review test files for usage patterns
- Look at existing provider implementations

Thank you for contributing!
