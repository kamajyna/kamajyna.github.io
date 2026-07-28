import urllib.request
import urllib.parse
import argparse
import sys

def submit_to_google(sitemap_url):
    print(f"[Google] Submitting sitemap: {sitemap_url}")
    # Google ping URL: http://www.google.com/ping?sitemap=URL
    ping_url = f"http://www.google.com/ping?sitemap={urllib.parse.quote(sitemap_url)}"
    try:
        response = urllib.request.urlopen(ping_url)
        if response.status == 200:
            print("[Google] Successfully submitted sitemap.")
        else:
            print(f"[Google] Failed with status: {response.status}")
    except Exception as e:
        print(f"[Google] Error submitting sitemap: {e}")

def submit_to_bing(sitemap_url):
    print(f"[Bing] Submitting sitemap: {sitemap_url}")
    # Bing ping URL: http://www.bing.com/ping?sitemap=URL
    ping_url = f"http://www.bing.com/ping?sitemap={urllib.parse.quote(sitemap_url)}"
    try:
        response = urllib.request.urlopen(ping_url)
        if response.status == 200:
            print("[Bing] Successfully submitted sitemap.")
        else:
            print(f"[Bing] Failed with status: {response.status}")
    except Exception as e:
        print(f"[Bing] Error submitting sitemap: {e}")

def main():
    parser = argparse.ArgumentParser(description="SEO Sitemap Submitter")
    parser.add_argument("--sitemap", required=True, help="Full URL to the sitemap.xml")
    args = parser.parse_args()

    submit_to_google(args.sitemap)
    submit_to_bing(args.sitemap)
    
    # Note: Naver Search Advisor usually requires manual registration of the sitemap
    # or using their specific webmaster API, but pinging Google/Bing covers the majority.
    print("SEO Sitemap submission sequence completed.")

if __name__ == "__main__":
    main()
