# Simple Web Crawler for Images

A simple, interactive Python script to crawl a website and download all unique images found within a specified depth.

## Features

- **Interactive Prompts:** If you don't provide command-line arguments, the script will interactively ask you for the target URL and the directory to save images.
- **Dependency Checking:** Automatically checks for required packages (`requests`, `beautifulsoup4`, `tqdm`) and prompts you to install them if they are missing.
- **Web Crawling:** Recursively crawls the website up to a specified depth to find all linked pages.
- **Image Extraction:** Scans each crawled page for image URLs, handling lazy-loaded images (using `data-src` or `data-lazyload` attributes).
- **Progress Bars:** Displays progress for both crawling pages and downloading images.
- **Failsafes:**
    - Avoids re-crawling the same page.
    - Avoids downloading the same image multiple times.
    - Validates content-type to ensure only actual images are saved.

## How to Use

### Prerequisites

- Python 3

### Running the Script

1.  Clone the repository or download the `simple-web-crawler.py` script.
2.  Open your terminal or command prompt and navigate to the directory where the script is located.
3.  Run the script using one of the following methods:

#### Interactive Mode

To be prompted for the URL and save location, simply run the script without any arguments:

```bash
python simple-web-crawler.py
```

The script will then ask you for the website URL and the directory where you want to save the images.

#### Command-Line Arguments

You can also provide arguments directly from the command line:

```bash
python simple-web-crawler.py <URL> -o <OUTPUT_DIRECTORY> -d <DEPTH>
```

**Example:**

```bash
python simple-web-crawler.py https://www.example.com -o C:\my_images -d 3
```

### Command-Line Options

- `URL`: (Optional) The base URL of the website to scrape. If not provided, the script will ask for it.
- `-o`, `--output`: (Optional) The directory to save the scraped images. If not provided, the script will ask for it.
- `-d`, `--depth`: (Optional) The maximum depth to crawl the website. Defaults to `2`.
