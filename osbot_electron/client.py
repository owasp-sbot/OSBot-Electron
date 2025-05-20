import asyncio
from playwright.async_api import async_playwright
import subprocess
import time

async def main():
    # Path to your Electron app
    electron_app_path = "../electron_app"  # Replace with the path to your Electron app folder

    # Start the Electron app as a subprocess
    process = subprocess.Popen(
        ["npm", "start"],
        cwd=electron_app_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Give the app a moment to start
    time.sleep(1)

    async with async_playwright() as p:
        # Connect to the running Electron app
        electron_app = await p.chromium.connect_over_cdp("http://localhost:9222")

        # Get the first context and page
        default_context = electron_app.contexts[0]
        page = default_context.pages[0]

        # Now you can interact with the page
        print("Connected to Electron app")
        print(f"Current URL: {page.url}")


        target_site= 'http://localhost:8000'
        target_site = "https://mvp.myfeeds.ai/aaaa"
        await page.goto(target_site)                    #open a page
        # Take a screenshot
        await page.screenshot(path="electron_app_screenshot.png", full_page=True)
        print(f"Saved screenshot to: {page.url}")

        # Close the browser
        await electron_app.close()

    # Terminate the Electron process
    process.terminate()
    process.wait()

if __name__ == "__main__":
    asyncio.run(main())