# Royal Analyzer AI

Autonomous Python 3.12 / PySide6 desktop application scaffold for statistical
analysis of Royal game result sequences.

The application is designed as modular packages for collection, SQLite history,
statistics, pattern mining, predictors, backtesting, and GUI rendering. Forecasts
are informational and based on accumulated historical statistics; they do not
claim or guarantee a betting advantage.

## Modules

- `collectors`: Playwright DOM probing, keepalive actions, OCR fallback hooks.
- `database`: SQLite roll history repository.
- `statistics`: frequencies, entropy, rolling values, transition matrices.
- `patterns`: n-grams and association-mining primitives.
- `predictors`: common `fit/predict/score/reset/save/load` interface.
- `backtesting`: historical simulations and drawdown/profit metrics.
- `gui`: PySide6 dark dashboard shell.

## Development

```bash
python -m pytest
```

## Build

See [BUILD.md](BUILD.md).
