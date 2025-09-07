# Microsoft 365 License Report Generator

Python script to fetch Microsoft 365 user license assignments via Microsoft Graph API.  
Exports results into a CSV report for admins to track license usage and compliance.

## Features
- Fetch users with their license details
- Export to CSV
- Supports filtering (licensed/unlicensed users)

## Requirements
- Python 3.9+
- msal, requests
- Azure AD App Registration with:
  - `User.Read.All`
  - `Directory.Read.All`

## Usage
```bash
python m365_license_report.py --tenant-id <TENANT_ID> --client-id <CLIENT_ID> --client-secret <SECRET>
