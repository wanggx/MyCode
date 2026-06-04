# Specification: Stock Platform

## Purpose

Define the behavioral contract for the stock data analysis platform, covering A-share and HK stock market data acquisition, technical indicator computation, multi-strategy stock selection, user authentication, and notification capabilities. This specification serves as the single source of truth for what the system currently does.

## Requirements

### Requirement: System Health Check

The system SHALL expose a health check endpoint to verify service availability.

#### Scenario: Health probe succeeds
- **WHEN** a client sends a GET request to `/api/health`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response body SHALL contain `status` field with value `healthy`

### Requirement: User Registration

The system SHALL allow new users to create an account with username and password.

#### Scenario: Register with valid credentials
- **GIVEN** a username that does not exist in the system
- **WHEN** a client sends a POST request to `/api/user/register` with body `{"username": "newuser", "password": "pass123"}`
- **THEN** the system SHALL respond with HTTP 201
- **AND** the response body SHALL contain `message` field with value `注册成功`

#### Scenario: Register with duplicate username
- **GIVEN** a username that already exists in the system
- **WHEN** a client sends a POST request to `/api/user/register` with the existing username
- **THEN** the system SHALL respond with HTTP 400
- **AND** the response body SHALL contain `error` field indicating duplicate username

#### Scenario: Register with missing fields
- **WHEN** a client sends a POST request to `/api/user/register` without `username` or `password`
- **THEN** the system SHALL respond with HTTP 400
- **AND** the response body SHALL contain `error` field indicating missing required fields

### Requirement: User Login

The system SHALL authenticate users and issue JWT tokens.

#### Scenario: Login with correct credentials
- **GIVEN** a registered user with username `admin` and password `123456`
- **WHEN** a client sends a POST request to `/api/user/login` with body `{"username": "admin", "password": "123456"}`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response body SHALL contain `data.token` as a non-empty JWT string
- **AND** the response body SHALL contain `data.user` with `id`, `username`, `email`, `role` fields

#### Scenario: Login with wrong password
- **GIVEN** a registered user
- **WHEN** a client sends a POST request to `/api/user/login` with incorrect password
- **THEN** the system SHALL respond with HTTP 401
- **AND** the response body SHALL contain `error` field indicating wrong credentials

#### Scenario: Login with missing fields
- **WHEN** a client sends a POST request to `/api/user/login` without `username` or `password`
- **THEN** the system SHALL respond with HTTP 400

### Requirement: User Info Retrieval

The system SHALL return authenticated user's profile information.

#### Scenario: Get info with valid token
- **GIVEN** a valid JWT token issued during login
- **WHEN** a client sends a GET request to `/api/user/info` with `Authorization: Bearer <token>`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response body SHALL contain `data` with user profile fields

#### Scenario: Get info without token
- **WHEN** a client sends a GET request to `/api/user/info` without Authorization header
- **THEN** the system SHALL respond with HTTP 401

### Requirement: Password Change

The system SHALL allow authenticated users to change their password.

#### Scenario: Change password with correct old password
- **GIVEN** an authenticated user
- **WHEN** a client sends a POST request to `/api/user/change-password` with valid `old_password` and `new_password` (>= 6 chars)
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response body SHALL contain `success` field with value `true`

#### Scenario: Change password with wrong old password
- **GIVEN** an authenticated user
- **WHEN** a client sends a POST request to `/api/user/change-password` with incorrect `old_password`
- **THEN** the system SHALL respond with HTTP 400
- **AND** the response body SHALL contain `error` field indicating wrong password

### Requirement: Stock List Query

The system SHALL return paginated stock list with optional filtering.

#### Scenario: Query with default pagination
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stocks`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response body SHALL contain `data.stocks` as an array
- **AND** the response SHALL contain `data.total`, `data.page`, `data.page_size`, `data.total_pages`

#### Scenario: Query with keyword filter
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stocks?keyword=茅台`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response `data.stocks` SHALL only contain stocks matching the keyword in `ts_code`, `symbol`, or `name`

#### Scenario: Query with area and industry filters
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stocks?area=北京&industry=银行`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response `data.stocks` SHALL only contain stocks matching both filters

### Requirement: Stock Area and Industry Listing

The system SHALL return distinct lists of stock areas and industries.

#### Scenario: Get areas
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stocks/areas`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response `data` SHALL be an array of distinct area strings

#### Scenario: Get industries
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stocks/industries`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response `data` SHALL be an array of distinct industry strings

### Requirement: Stock Daily Data Query

The system SHALL return paginated daily/weekly/monthly price data for a given stock.

#### Scenario: Query daily data
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stock/data?ts_code=000001.SZ&startDate=20250101&endDate=20250601&type=d`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response `data.items` SHALL contain price records with fields: `ts_code`, `trade_date`, `open`, `high`, `low`, `close`, `pre_close`, `change`, `pct_chg`, `vol`

#### Scenario: Query weekly data
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stock/data?ts_code=000001.SZ&startDate=20250101&endDate=20250601&type=w`
- **THEN** the system SHALL query the `stock_week` table and return weekly aggregated data

#### Scenario: Missing required parameters
- **GIVEN** an authenticated user
- **WHEN** a client sends a GET request to `/api/stock/data` without `ts_code`, `startDate`, or `endDate`
- **THEN** the system SHALL respond with HTTP 400

### Requirement: Stock Sync

The system SHALL synchronize stock basic information from Tushare.

#### Scenario: Sync stocks
- **GIVEN** an authenticated user
- **WHEN** a client sends a POST request to `/api/stocks/sync`
- **THEN** the system SHALL call Tushare API to refresh the stock list
- **AND** the system SHALL respond with a JSON result indicating success or failure

### Requirement: Stock Selection Query

The system SHALL return paginated stock selection results for a given date, with automatic async selection if no data exists.

#### Scenario: Query with existing data
- **GIVEN** an authenticated user
- **GIVEN** stock selection data exists for the requested date
- **WHEN** a client sends a GET request to `/api/stock_select?select_date=20260101`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response `data.items` SHALL contain selection records with fields: `select_date`, `ts_code`, `name`, `vol`, `trend3`, `trend5`, `trend10`, `trend20`, `trend30`

#### Scenario: Query triggers async selection when data is empty
- **GIVEN** an authenticated user
- **GIVEN** no stock selection data exists for the requested date
- **WHEN** a client sends a GET request to `/api/stock_select?select_date=20260101`
- **THEN** the system SHALL start an async selection task in a background thread
- **AND** the system SHALL respond with HTTP 200 indicating selection is in progress

#### Scenario: Reselect forces re-selection
- **GIVEN** an authenticated user
- **GIVEN** stock selection data exists for the requested date
- **WHEN** a client sends a GET request to `/api/stock_select?select_date=20260101&reselect=true`
- **THEN** the system SHALL delete existing records for that date
- **AND** the system SHALL start a new async selection task

### Requirement: Mock Stock Selection

The system SHALL return selection indicators for a single stock.

#### Scenario: Mock select a stock
- **GIVEN** an authenticated user
- **WHEN** a client sends a POST request to `/api/stock/select/mock` with body `{"ts_code": "000001.SZ", "date_str": "20260101"}`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response SHALL contain the stock's technical indicators as a JSON string

### Requirement: Volume Line Data

The system SHALL return daily stock selection counts within a date range.

#### Scenario: Get volume line data
- **WHEN** a client sends a GET request to `/api/vol_line?startDate=20260101&endDate=20260131`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response `data` SHALL be an array of `{select_date, count}` records

### Requirement: Data Integrity Check

The system SHALL return daily data coverage statistics.

#### Scenario: Check data coverage
- **WHEN** a client sends a GET request to `/api/stock/check?startDate=20260101&endDate=20260131`
- **THEN** the system SHALL respond with HTTP 200
- **AND** the response SHALL contain paginated daily record counts

### Requirement: Data Backfill

The system SHALL asynchronously download missing daily/weekly/monthly data for a date range.

#### Scenario: Backfill daily data
- **WHEN** a client sends a POST request to `/api/stock/daily/add` with body `{"start_date": "20260101", "end_date": "20260105", "type": "d"}`
- **THEN** the system SHALL validate that the date range does not exceed 30 days for daily type
- **AND** the system SHALL start an async download task
- **AND** the system SHALL respond with HTTP 200 indicating the task has been submitted

#### Scenario: Backfill with invalid date format
- **WHEN** a client sends a POST request to `/api/stock/daily/add` with non-yyyyMMdd date format
- **THEN** the system SHALL respond with error indicating invalid date format

### Requirement: Scheduled Daily Download

The system SHALL automatically download stock data at a scheduled time each day.

#### Scenario: Daily scheduler triggers
- **GIVEN** the system is running
- **WHEN** the system clock reaches 16:30 on a trading day
- **THEN** the system SHALL download A-share daily data from Tushare
- **THEN** the system SHALL aggregate weekly and monthly data
- **THEN** the system SHALL run stock selection algorithms
- **THEN** the system SHALL download HK stock daily data
- **THEN** the system SHALL send completion notification via WeChat

### Requirement: WeChat Notification

The system SHALL send stock selection results and status messages via WeChat Work bot.

#### Scenario: Send selection results
- **WHEN** stock selection completes successfully
- **THEN** the system SHALL send a text message with the selection summary to the configured WeChat Work webhook

#### Scenario: Send error notification
- **WHEN** scheduled download or selection encounters an exception
- **THEN** the system SHALL send an error message to the configured WeChat Work webhook

### Requirement: Authentication Middleware

The system SHALL protect authenticated endpoints with Bearer JWT validation.

#### Scenario: Access protected endpoint with valid token
- **GIVEN** a valid JWT token
- **WHEN** a client accesses a protected route
- **THEN** the system SHALL decode and verify the token
- **AND** the system SHALL attach user payload to the request context

#### Scenario: Access protected endpoint with expired token
- **GIVEN** an expired JWT token
- **WHEN** a client accesses a protected route
- **THEN** the system SHALL respond with HTTP 401
- **AND** the response SHALL indicate invalid or expired token

### Requirement: Stock Selection Algorithms

The system SHALL execute multiple selection strategies and merge results.

#### Scenario: Volume magnify selection
- **WHEN** the volume magnify strategy runs
- **THEN** the system SHALL compute volume slope (3/5/10/20/30-day) for each stock
- **THEN** the system SHALL filter stocks with significant volume magnification
- **THEN** the system SHALL save results to `stock_select` table

#### Scenario: MA trend selection
- **WHEN** the MA trend strategy runs
- **THEN** the system SHALL compute MA3/MA5 crossovers for daily and weekly data
- **THEN** the system SHALL merge MACD/KDJ golden cross indicators
- **THEN** the system SHALL save merged results to `stock_trend_select` table

#### Scenario: HK stock selection
- **WHEN** the HK stock selection strategy runs
- **THEN** the system SHALL run volume magnify and trend analysis on HK stock data
- **THEN** the system SHALL export results to CSV files
