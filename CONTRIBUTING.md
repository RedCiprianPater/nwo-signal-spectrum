# Contributing to NWO Signal Spectrum

Thank you for your interest in contributing!

## Development Setup

1. Fork the repository
2. Clone your fork
3. Install dependencies:
   ```bash
   composer install
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure
5. Start Docker services:
   ```bash
   docker-compose up -d
   ```

## Code Standards

### PHP
- Follow PSR-12 coding standards
- Run `composer style` to check
- Run `composer style-fix` to auto-fix

### Python
- Follow PEP 8
- Use type hints where possible
- Run `black` for formatting

### Testing
```bash
# PHP tests
composer test

# Python tests
pytest

# Static analysis
composer analyse
```

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Ensure all checks pass:
   ```bash
   composer check
   ```
6. Submit PR with clear description

## Commit Messages

Use conventional commits:
- `feat: Add new signal type`
- `fix: Correct frequency calculation`
- `docs: Update API documentation`
- `test: Add apocalypse indicator tests`

## Questions?

- GitHub Issues: https://github.com/RedCiprianPater/nwo-signal-spectrum/issues
- Discord: https://discord.gg/nwo
