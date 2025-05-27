# Instagram Brute Force Tool

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

**Author:** hSECURITIES
**Version:** 1.0
**Last Updated:** [Current Date]

## ⚠️ Disclaimer

This tool is for **educational and authorized security testing purposes only**. The author and contributors are not responsible for any misuse or damage caused by this program. Only use this tool against systems you own or have explicit permission to test.

## Description

A Python-based brute force tool for Instagram that supports:
- Multi-threaded password attacks
- Proxy support for anonymity
- Resume functionality for interrupted attacks
- Customizable performance modes
- Database management for proxies

## Features

- **Multi-threaded attack**: Supports up to 32 concurrent attempts
- **Proxy support**: Rotate through proxies to avoid IP blocking
- **Session management**: Resume interrupted attacks
- **Performance modes**: Adjust based on your system capabilities
- **Proxy database**: Manage and prune proxy lists
- **Statistics tracking**: Monitor attack progress

## Requirements

- Python 3.6 or higher
- Required libraries (install with `pip install -r requirements.txt`):
  - `requests`
  - `colorama` (for colored output)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/instagram-brute-force.git
   cd instagram-brute-force
