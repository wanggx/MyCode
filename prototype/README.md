# Quant UI Prototype

This directory contains high-fidelity UI prototypes for the lightweight quant research platform.

## Recommended Prototype

- `quant-prototype-v2.html`: recommended interactive HTML prototype.
- `quant-prototype.html`: earlier compact prototype, kept only for comparison.
- `quant-ui-prototype-01.png`: original visual reference board.
- `quant-ui-prototype-02.png`: original visual reference board.

## Why v2

The compact 5-menu version felt too rough and too small for a professional quant research platform.

The v2 prototype returns to the structure of the first two PNG mockups:

1. Complete left navigation.
2. Top data-date and user bar.
3. Dense tables and charts.
4. Dedicated research, data, strategy, backtest, signal, portfolio, task, and settings areas.
5. No live trading, broker order, or capital account features.

## Navigation

The recommended v2 navigation:

1. Dashboard
2. Data Center
3. Factor Lab
4. Strategy Workspace
5. Backtest Center
6. Stock Signals
7. Portfolio Risk
8. Task Center
9. System Settings

The actual UI text in `quant-prototype-v2.html` is Chinese.

## Interactions Covered

`quant-prototype-v2.html` includes:

- Login and logout.
- Sidebar page switching.
- Dashboard jump to signal page.
- Data sync action.
- Factor analysis refresh action.
- Strategy selection.
- Save and run strategy action.
- Backtest task submission.
- Signal filtering.
- Signal detail drawer.
- Task execution action.

These are prototype interactions only and do not call real APIs.

## Product Boundary

First phase should focus on:

- Data quality and backfill.
- Factor research.
- Parameterized strategies.
- Daily-frequency backtesting.
- Explainable stock signals.
- Simulated portfolio risk.
- Scheduled tasks and notifications.

Do not include in phase one:

- Live trading.
- Broker order entry.
- Capital account management.
- Complex team permissions.
- Full notebook or online IDE.

## Suggested Vue Split

- `MainLayout.vue`
- `DashboardView.vue`
- `DataCenterView.vue`
- `FactorLabView.vue`
- `StrategyWorkspaceView.vue`
- `BacktestCenterView.vue`
- `StockSignalsView.vue`
- `PortfolioRiskView.vue`
- `TaskCenterView.vue`
- `SystemSettingsView.vue`

## Suggested API Contract

- `GET /api/dashboard/summary`
- `GET /api/data-quality`
- `POST /api/data/backfill`
- `GET /api/factors`
- `POST /api/factors/analyze`
- `GET /api/strategies`
- `POST /api/strategies/{id}/run`
- `POST /api/backtests`
- `GET /api/backtests/{id}`
- `GET /api/signals`
- `GET /api/signals/{code}`
- `GET /api/portfolio/risk`
- `GET /api/tasks`
- `POST /api/tasks/{id}/run`

## Technical Plan

The detailed single-service technical plan is documented here:

```text
docs/quant-platform/README.md
```

## Open

Open this file directly in a browser:

```text
prototype/quant-prototype-v2.html
```
