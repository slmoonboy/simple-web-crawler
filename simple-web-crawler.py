import sys
import subprocess
import importlib.util

# --- Dependency Checking ---
def check_dependencies():
    """
    Checks if all required packages are installed and prompts the user to install them if not.
    """
    required_packages = {
        "requests": "requests",
        "beautifulsoup4": "bs4",  # Check for 'bs4' module but install 'beautifulsoup4' package
        "tqdm": "tqdm"
    }
    missing_packages = []

    for install_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append(install_name)

    if missing_packages:
        print("Some required packages are not installed.")
        for pkg in missing_packages:
            print(f" - {pkg}")
        
        try:
            response = input("Do you want to try and install them now? (y/n): ").lower()
            if response == 'y':
                for pkg in missing_packages:
                    print(f"Installing {pkg}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                print("\nDependencies installed successfully.")
                print("Please restart the script to use the newly installed dependencies.")
                sys.exit(0)
            else:
                print("Please install the missing dependencies manually to run the script.")
                sys.exit(1)
        except Exception as e:
            print(f"An error occurred during installation: {e}")
            print("Please try installing the dependencies manually.")
            sys.exit(1)

# Run the check before importing the modules
check_dependencies()


import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re
import time
import argparse
from tqdm import tqdm

def sanitize_filename(filename):
    """
    Sanitizes a string to be used as a valid filename.
    """
    if not filename:
        return ""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_')
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def download_image(url, output_folder, headers):
    """
    Downloads a single image from a URL, returns True if successful or file exists, False otherwise.
    """
    try:
        a = urlparse(url)
        img_name = os.path.basename(a.path)

        if not img_name or img_name == '/':
            return False

        img_name = img_name.split('?')[0].split('#')[0]
        if not img_name:
            return False
        
        sanitized_name = sanitize_filename(img_name)
        if not sanitized_name:
            return False

        file_path = os.path.join(output_folder, sanitized_name)

        if os.path.exists(file_path):
            return True

        img_data = requests.get(url, headers=headers, timeout=20, stream=True)
        img_data.raise_for_status()
        
        content_type = img_data.headers.get('content-type')
        if not content_type or not content_type.lower().startswith('image'):
            return False

        total_size = int(img_data.headers.get('content-length', 0))
        
        with open(file_path, 'wb') as f, tqdm(
            desc=sanitized_name,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            leave=False
        ) as bar:
            for chunk in img_data.iter_content(chunk_size=1024):
                size = f.write(chunk)
                bar.update(size)
        return True
    except requests.exceptions.RequestException:
        return False
    except IOError:
        return False

def crawl_site(base_url, max_depth, headers):
    """
    Crawls the site and returns a set of all pages and a set of all unique image URLs.
    """
    domain_name = urlparse(base_url).netloc
    to_visit = [(base_url, 0)]
    visited = set()
    all_image_urls = set()

    print("Starting crawl to map the site...")
    
    with tqdm(desc="Crawling Pages", unit="page") as progress_bar:
        while to_visit:
            current_url, depth = to_visit.pop(0)

            if current_url in visited or depth > max_depth:
                continue

            progress_bar.set_description(f"Crawling (Depth {depth}): {current_url[-50:]}")
            visited.add(current_url)

            try:
                response = requests.get(current_url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            for img in soup.find_all('img'):
                img_url = img.get('data-src') or img.get('data-lazyload') or img.get('src')
                if not img_url or img_url.startswith('data:'):
                    continue
                
                absolute_img_url = urljoin(current_url, img_url)
                all_image_urls.add(absolute_img_url)

            if depth < max_depth:
                for link in soup.find_all('a', href=True):
                    absolute_link_url = urljoin(current_url, link['href'])
                    
                    if urlparse(absolute_link_url).netloc == domain_name and '#' not in absolute_link_url:
                        if absolute_link_url not in visited:
                            to_visit.append((absolute_link_url, depth + 1))
            
            progress_bar.update(1)
            time.sleep(0.5)

    print(f"\nCrawl finished. Found {len(visited)} pages and {len(all_image_urls)} unique image URLs.")
    return visited, all_image_urls

def main():
    """
    Main function to parse arguments and run the scraper.
    """
    parser = argparse.ArgumentParser(description="A simple web crawler to scrape images from a website.")
    parser.add_argument("url", nargs='?', help="The base URL of the website to scrape.")
    parser.add_argument("-o", "--output", help="The directory to save the scraped images.")
    parser.add_argument("-d", "--depth", type=int, default=2, help="The maximum depth to crawl. Defaults to 2.")
    args = parser.parse_args()

    # --- Interactive Prompts ---
    base_url = args.url
    if not base_url:
        while not base_url:
            base_url = input("Please enter the website URL you want to crawl: ")
            if not base_url:
                print("URL cannot be empty.")
    
    if not base_url.startswith("http"):
        base_url = "https://" + base_url
    print(f"Using URL: {base_url}")

    output_directory = args.output
    if not output_directory:
        while not output_directory:
            output_directory = input("Please enter the directory to save the images (e.g., 'scrapes'): ")
            if not output_directory:
                print("Output directory cannot be empty.")
    print(f"Saving images to: {output_directory}")
    
    max_depth = args.depth

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            print(f"Created directory: {output_directory}")
        except OSError as e:
            print(f"Error creating directory {output_directory}: {e}")
            sys.exit(1)
    else:
        print(f"Output directory '{output_directory}' already exists.")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    _, all_image_urls = crawl_site(base_url, max_depth, headers)
    
    print("\nStarting image downloads...")
    
    download_count = 0
    with tqdm(list(all_image_urls), desc="Downloading Images", unit="file") as image_progress:
        for img_url in image_progress:
            if download_image(img_url, output_directory, headers):
                download_count += 1
    
    print(f"\nDownload process complete. Successfully downloaded or found {download_count} images in '{output_directory}'.")


if __name__ == "__main__":
    main()