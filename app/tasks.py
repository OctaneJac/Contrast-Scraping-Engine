import subprocess

def run_spider(spider_name):
    try:
        # Trigger Scrapy spider as a subprocess
        result = subprocess.run(
            ["scrapy", "crawl", spider_name],
            cwd="scraper_archive",  # Path to the Scrapy project
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return str(e)
