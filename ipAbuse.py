import requests
import ipaddress
import argparse
import json
import time
import os
import fcntl
import csv

api_keys = [
    "replace with your key",
    "replace with another key key"
]

index_file = "key_index.txt"
cache_file = "cache.json"
ip_cache = {}


def current_milli_time():
    return round(time.time() * 1000)


# Load cache from file if available
if os.path.exists(cache_file):
    with open(cache_file, "r") as f:
        try:
            ip_cache = json.load(f)
        except json.JSONDecodeError:
            ip_cache = {}


def save_cache():
    with open(cache_file, "w") as f:
        json.dump(ip_cache, f, indent=4)


def get_next_api_key():
    with open(index_file, "a+") as f:
        f.seek(0)
        try:
            fcntl.flock(f, fcntl.LOCK_EX)
            idx_str = f.read().strip()
            last_index = int(idx_str) if idx_str.isdigit() else -1
            next_index = (last_index + 1) % len(api_keys)
            f.seek(0)
            f.truncate()
            f.write(str(next_index))
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return api_keys[next_index]


def check_ip(ip, days):
    # Check cache first
    if ip in ip_cache:
        return ip_cache[ip]

    try:
        if ipaddress.ip_address(ip).is_private:
            return {"ipAddress": ip, "usageType": "Private IP Address", "countryCode": "None", "isp": "None", "domain": "None", "totalReports": "None"}
    except ValueError:
        return {"ipAddress": ip, "message": "Invalid IP address"}

    api_key = get_next_api_key()

    headers = {
        'Key': api_key,
        'Accept': 'application/json',
    }

    params = {
        'ipAddress': ip,
        'maxAgeInDays': days
    }

    while True:
        try:
            response = requests.get('https://api.abuseipdb.com/api/v2/check', headers=headers, params=params)
            if response.status_code == 503:
                print(f"Error: AbuseIPDB returned a 503 for {ip}. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                break
        except requests.RequestException as e:
            print(f"Error connecting to AbuseIPDB: {e}")
            return {"ipAddress": ip, "message": f"Connection error: {e}"}

    data = response.json()

    if 'errors' in data:
        return {"ipAddress": ip, "message": f"Error: {data['errors'][0]['detail']}"}

    ip_cache[ip] = data['data']
    save_cache()
    return data['data']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check IP reputation using AbuseIPDB")
    parser.add_argument("--ip", help="The IP address to check")
    parser.add_argument("--file", help="A file containing a list of IP addresses to check")
    parser.add_argument("--days", type=int, default=30, help="Max age of reports in days (default: 30)")
    parser.add_argument("--cloudCheck", action="store_true", help="Export CSV of results containing Cloud/Data Center/Web Hosting")
    parser.add_argument("--out", help="Output CSV file (if not provided, a timestamped file will be used)")
    args = parser.parse_args()

    if args.ip and args.file:
        print("Error: Use either --ip or --file, not both.")
        exit(1)

    results = []

    if args.ip:
        result = check_ip(args.ip.strip(), args.days)
        print(json.dumps(result, indent=4))
        results.append(result)

    elif args.file:
        if not os.path.isfile(args.file):
            print(f"Error: File {args.file} does not exist.")
            exit(1)

        with open(args.file, "r") as f:
            seen = set()
            for line in f:
                ip = line.strip()
                if not ip or ip in seen:
                    continue
                seen.add(ip)
                result = check_ip(ip, args.days)
                print(json.dumps(result, indent=4))
                results.append(result)

    else:
        print("Error: You must provide either --ip or --file.")
        exit(1)

    # Cloud/Data Center/Web Hosting Check + CSV Export
    if args.cloudCheck and results:
        out_file = args.out if args.out else f"cloud_check_{current_milli_time()}.csv"
        

        # Sa adaug try catch
        with open(out_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["IP Address", "Usage Type", "Country", "ISP", "Domain", "Total Reports"])
            for r in results:
                try:
                    if not isinstance(r, dict):
                        continue
                    usage = r.get("usageType", "")
                    if any(x in usage.lower() for x in ["cloud", "data center", "transit", "web hosting", "content delivery network"]):
                        writer.writerow([
                            r.get("ipAddress", ""),
                            usage,
                            r.get("countryCode", ""),
                            r.get("isp", ""),
                            r.get("domain", ""),
                            r.get("totalReports", 0)
                        ])
                except:
                    continue
        print(f"[+] Cloud/Data Center/Web Hosting results saved to: {out_file}")
