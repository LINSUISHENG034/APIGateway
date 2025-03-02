# AI Proxy API Reference

## Overview

This document provides detailed information about the AI Proxy API endpoints.

## Endpoints

### GET /providers
- Description: Lists all registered providers
- Response: JSON array of provider objects

### POST /providers
- Description: Registers a new provider
- Request Body:
  ```json
  {
    "name": "Provider Name",
    "endpoint": "https://provider.endpoint.com",
    "api_key": "your_api_key"
  }
  ```
- Response: JSON object with provider details

## Additional Information

More documentation will be added as the API develops.