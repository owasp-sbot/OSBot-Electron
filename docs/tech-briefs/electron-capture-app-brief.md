# Project Brief: Electron-Based Web Content Capture App

## Project Goals and Scope

The goal of this project is to build a cross-platform desktop application that reproduces and extends the functionality of the original Chrome extension for capturing full web content. Key objectives include:

- **Full Content Capture**: Monitor all web page loads in an embedded Chromium browser and capture everything the page loads, including the HTML, all JavaScript files, CSS, AJAX/XHR responses, and other resources, in real time.

- **Preserve and Archive Web Pages**: Store a complete snapshot of each visited page for authorized or target domains (e.g., partner news sites) – including the DOM HTML and loaded scripts – to enable future analysis like fact-checking, provenance verification, or content replay.

- **Content Hashing & Deduplication**: Compute a unique hash (e.g., SHA-256) of the captured content to fingerprint each page and avoid storing duplicates.

- **Client-Side Processing with Python**: Leverage a built-in Python engine to process captures on the client side (the desktop app) as much as possible.

- **Serverless Backend for Storage**: Use a minimal FastAPI backend (deployable as a serverless function or lightweight service) that simply receives content from the app and stores it in AWS S3.

- **Structured Cloud Storage**: Organize stored pages in S3 with a timestamp-based key schema and maintain a JSON index of captures.

- **Dual Operation Modes**: Support both production mode (syncing to cloud) and development/offline mode (using local services).

- **Cross-Platform Desktop App**: Package the system as a user-friendly desktop application using Electron.

In scope for this project is the development of the Electron app, integration of the Python/Playwright capture engine, the serverless FastAPI backend, and the offline mode setup. Out of scope are any analysis or UI features beyond the capture itself.

## High-Level Architecture and Components

![High-level system architecture of the Electron-based capture app]

The system is composed of several key components working in tandem:

### Electron Desktop Application (Chromium UI)

- **Embedded Chromium Browser**: The app's main window is essentially a Chromium browser instance where users can navigate normally.
  
- **Navigation Controls and UX**: Basic browser controls (address bar, back/forward buttons, etc.) for usability.
  
- **Integration with Python Backend**: Electron's main process coordinates with the Python process.
  
- **Browser Context Configuration**: Configuration to ensure proper permissions and access.

### Playwright Python Capture Engine

- **Browser Automation & Monitoring**: Playwright connects to the Chromium instance and monitors page loads, capturing content.
  
- **Data Packaging and Processing**: Python code packages captured data for upload.
  
- **Content Hashing & Dedup in Python**: Compute content hashes to identify duplicates.
  
- **Real-Time Content Rewriting (Optional)**: Support for optional real-time page manipulation.
  
- **Reuse of Python Ecosystem**: Leverage the full Python ecosystem for processing.
  
- **"Write Once, Run Anywhere" Logic**: Maintain consistent logic between client and server contexts.

### FastAPI Serverless Backend

- **Capture API Endpoint**: Receives uploaded content from the desktop app.
  
- **Index Management**: Updates the index file tracking all captures.
  
- **Deduplication Check Endpoint (Optional)**: API to check if content has been captured before.
  
- **Stateless and Scalable**: No persistent state, easy to scale.
  
- **CORS and Integration**: Configured to allow the Electron app to communicate with it.

### AWS S3 Storage and Indexing

- **Timestamp-Based Storage Structure**: Organized key naming based on capture time.
  
- **Index File**: JSON file containing metadata for each capture.
  
- **LocalStack for Offline Storage**: Local emulation of S3 for development.
  
- **Retention and Volume**: Considerations for data growth over time.

## Production vs. Offline Mode Details

The application will support two operation modes:

### Production Mode
- Uses cloud backend and real AWS S3
- For end-users or live environments
- Requires network connectivity and valid credentials

### Offline Development Mode
- Everything runs locally
- Uses LocalStack for S3 emulation
- Enables development without cloud costs or connectivity
- Identical behavior from user perspective

## Rationale for Using Electron + Chromium + Playwright + Python

This tech stack was chosen to maximize cross-platform support, developer productivity, and to overcome limitations of the previous browser extension approach:

- **Electron**: Provides cross-platform desktop app capabilities with embedded Chromium
- **Embedded Chromium**: Ensures consistent browser environment under our control
- **Playwright**: Offers powerful browser automation with Python support
- **Python**: Leverages rich ecosystem and enables native code execution (faster than Pyodide)

## Advantages Over the Original Browser Extension Approach

1. **Greater Control Over Browser Environment**: Not limited by extension APIs
2. **Elimination of Pyodide Overhead**: Native Python execution is faster
3. **Cross-Browser and Future-Proofing**: Less tied to Chrome-specific features
4. **Distribution and Usage Simplicity**: Easier installation for users
5. **UI/UX Enhancements**: Ability to create custom interfaces
6. **Integrated Testing and CI**: Better automation capabilities
7. **Fewer Security Headaches**: Different threat model with better isolation
8. **Customization and Extensibility**: Easier to extend functionality

## Security, Performance, and Extensibility Considerations

### Security
- Whitelist-only domain capture
- HTTPS transport and encrypted storage
- Electron security best practices implementation
- Stateless backend with minimal attack surface
- Sandboxing for content viewing

### Performance
- Asynchronous processing to avoid UI blocking
- Efficient data handling with streaming when possible
- Fast native hashing algorithms
- Memory usage monitoring
- Network bandwidth considerations
- Local caching options

### Extensibility
- Modular architecture allowing independent component updates
- Extensible Python capture logic for different content types
- Flexible backend deployment options
- Upgradeable indexing mechanisms
- Support for future integrations with analysis systems

## Development and Testing Workflow

The development workflow includes:

- **Project Structure**: Organized repository with Electron, Python, and backend code
- **Running in Development**: Scripts to launch all components locally
- **Playwright Integration**: Using Playwright for both app functionality and testing
- **Unit Testing**: Tests for core functionality without browser dependencies
- **Integration Testing**: End-to-end tests using offline mode
- **Playwright Test Scenarios**: Testing various user interaction patterns
- **LocalStack in CI**: Cloud emulation for continuous integration
- **Backend Testing**: Independent verification of API functionality
- **Developer Environment**: Documentation for setup and development
- **Continuous Integration**: Automated build and test on commits
- **Version Control & Releases**: Managed releases with proper versioning
