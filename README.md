# SQL Injection Scanner Testing Environment

This repository contains a SQL injection scanner and a deliberately vulnerable web application for testing purposes.

## ⚠️ SECURITY WARNING
The vulnerable web application (`vulnerable_app.py`) contains intentional security flaws and should **NEVER** be deployed in production or on public servers. Use only for educational purposes in isolated environments.

## Files Overview

- `sql.py` - Advanced SQL injection scanner
- `vulnerable_app.py` - Deliberately vulnerable Flask web application
- `test_scanner.py` - Automated test script
- `setup.py` - Dependency installation script
- `requirements.txt` - Scanner dependencies
- `app_requirements.txt` - Web app dependencies

## Quick Start

### 1. Install Dependencies
```bash
python setup.py
```

### 2. Run Automated Test
```bash
python test_scanner.py
```

This will:
- Start the vulnerable web application on `http://localhost:5000`
- Run the SQL injection scanner against it
- Generate reports (HTML, PDF, DOCX)
- Clean up automatically

## Manual Testing

### Start the Vulnerable Application
```bash
python vulnerable_app.py
```

The app will be available at `http://localhost:5000`

### Run the Scanner
```bash
python sql.py -u http://localhost:5000 -d 2 -w 10 -f all
```

## Vulnerable Endpoints

The test application includes several intentionally vulnerable endpoints:

### 1. Login (GET & POST)
- **URL**: `/login`
- **Vulnerable Parameters**: `username`, `password`
- **Test**: `/login?username=admin'--&password=anything`

### 2. Product Search
- **URL**: `/search?q=<query>`
- **Vulnerable Parameter**: `q`
- **Test**: `/search?q=' OR 1=1--`

### 3. User Profile
- **URL**: `/user?id=<id>`
- **Vulnerable Parameter**: `id`
- **Test**: `/user?id=1' UNION SELECT 1,2,3,4--`

### 4. News Filter
- **URL**: `/news?category=<category>`
- **Vulnerable Parameter**: `category`
- **Test**: `/news?category=' OR 1=1--`

## Scanner Features

The SQL injection scanner includes:

- **Web Crawling**: Automatically discovers URLs
- **GET Parameter Testing**: Tests URL parameters for SQL injection
- **POST Form Testing**: Tests form inputs for SQL injection
- **WAF Detection**: Identifies common Web Application Firewalls
- **Multi-threading**: Fast concurrent scanning
- **Report Generation**: HTML, PDF, and DOCX reports
- **Error-based Detection**: Identifies SQL errors in responses
- **Time-based Detection**: Tests for time-delay SQL injection
- **Boolean-based Detection**: Tests for boolean-based blind SQL injection

## Scanner Usage

```bash
python sql.py -u <target_url> [options]

Options:
  -u, --url URL         Base URL to scan (required)
  -d, --depth DEPTH     Crawl depth (default: 2)
  -w, --workers WORKERS Number of threads (default: 10)
  -f, --format FORMAT   Report format: html, pdf, docx, all (default: all)
```

## Example Test Cases

### Basic SQL Injection Tests
```bash
# Test login bypass
curl "http://localhost:5000/login?username=admin'--&password=test"

# Test UNION injection
curl "http://localhost:5000/user?id=1' UNION SELECT 1,2,3,4--"

# Test error-based injection
curl "http://localhost:5000/search?q='"

# Test time-based injection
curl "http://localhost:5000/search?q=' OR SLEEP(5)--"
```

### Scanner Tests
```bash
# Quick scan
python sql.py -u http://localhost:5000 -d 1 -w 5

# Deep scan with more threads
python sql.py -u http://localhost:5000 -d 3 -w 20

# Generate only HTML report
python sql.py -u http://localhost:5000 -f html
```

## Expected Results

When running the scanner against the vulnerable application, you should expect to find:

1. **SQL injection in login form** (GET and POST methods)
2. **SQL injection in search functionality**
3. **SQL injection in user profile lookup**
4. **SQL injection in news filtering**
5. **Various SQL error messages** indicating successful detection

## Troubleshooting

### Common Issues

1. **Port 5000 already in use**
   - Kill any existing Flask processes
   - Or modify the port in `vulnerable_app.py`

2. **Missing dependencies**
   - Run `python setup.py` again
   - Install packages manually: `pip install flask requests beautifulsoup4`

3. **Scanner not finding vulnerabilities**
   - Ensure the vulnerable app is running
   - Check if the URLs are being crawled correctly
   - Verify network connectivity

### Debugging

- Check if the app is accessible: `curl http://localhost:5000`
- View app logs in the terminal where `vulnerable_app.py` is running
- Use `-w 1` to run scanner with single thread for easier debugging

## Educational Value

This setup demonstrates:
- How SQL injection vulnerabilities are introduced
- How automated scanners detect these vulnerabilities
- The importance of input validation and parameterized queries
- WAF detection techniques
- Report generation for security assessments

## Security Best Practices

To prevent SQL injection in real applications:
1. Use parameterized queries/prepared statements
2. Implement input validation
3. Use ORM frameworks that provide protection
4. Apply principle of least privilege to database accounts
5. Implement Web Application Firewalls (WAF)
6. Regular security testing and code reviews

## Disclaimer

This tool is for educational and authorized testing purposes only. Users are responsible for complying with applicable laws and regulations. The authors are not responsible for any misuse of this tool.
