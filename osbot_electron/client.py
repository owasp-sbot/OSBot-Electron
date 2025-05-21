import asyncio
from playwright.async_api import async_playwright
import subprocess
import time
import sys
import json
import os

async def main():
    # Get debug port from command line arguments
    debug_port = int(sys.argv[1]) if len(sys.argv) > 1 else 9222

    async with async_playwright() as p:
        try:
            # Connect to the running Electron app
            electron_app = await p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")

            # Get the first context and page
            default_context = electron_app.contexts[0]
            page = default_context.pages[0]

            # Now you can interact with the page
            print(f"Connected to Electron app on port {debug_port}")
            print(f"Current URL: {page.url}")

            # Example: Navigate to a website and capture content
            target_site = "https://docs.diniscruz.ai"
            await page.goto(target_site)

            # Capture page content
            html_content = await page.content()

            # Save the content to a file
            with open("captured_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            # Take a screenshot
            await page.screenshot(path="screenshot.png", full_page=True)
            print(f"Captured content from: {page.url}")
            print(f"Saved screenshot and HTML content")

            # Close the browser
            await electron_app.close()

        except Exception as e:
            print(f"Error connecting to Electron app: {e}")
            return 1

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)