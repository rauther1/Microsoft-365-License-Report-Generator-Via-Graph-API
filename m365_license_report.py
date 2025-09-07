"""
Microsoft 365 License Report Generator
--------------------------------------
Fetches all users and their assigned licenses from Microsoft Graph API.
Exports results into a CSV file.

Requirements:
    pip install msal requests

Azure AD App Registration:
    - Permissions: User.Read.All, Directory.Read.All (Application)
    - Authentication: Client Secret
"""

import csv
import argparse
import requests
import msal


GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"


def get_access_token(tenant_id, client_id, client_secret):
    """Authenticate using MSAL and return access token"""
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )
    scopes = ["https://graph.microsoft.com/.default"]
    token_result = app.acquire_token_for_client(scopes)
    if "access_token" in token_result:
        return token_result["access_token"]
    else:
        raise Exception(f"Failed to acquire token: {token_result}")


def fetch_users_with_licenses(token):
    """Fetch all users and their assigned licenses"""
    users = []
    url = f"{GRAPH_API_ENDPOINT}/users?$select=id,displayName,userPrincipalName,assignedLicenses,accountEnabled"

    headers = {"Authorization": f"Bearer {token}"}

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Graph API error: {response.text}")

        data = response.json()
        for user in data.get("value", []):
            license_skus = [lic["skuId"] for lic in user.get("assignedLicenses", [])]
            users.append({
                "UserPrincipalName": user.get("userPrincipalName"),
                "DisplayName": user.get("displayName"),
                "AccountEnabled": user.get("accountEnabled"),
                "AssignedLicenses": ", ".join(license_skus) if license_skus else "None"
            })

        url = data.get("@odata.nextLink", None)

    return users


def export_to_csv(users, output_file):
    """Export users with license info to CSV"""
    fieldnames = ["UserPrincipalName", "DisplayName", "AccountEnabled", "AssignedLicenses"]
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)


def main():
    parser = argparse.ArgumentParser(description="M365 License Report Generator")
    parser.add_argument("--tenant-id", required=True, help="Azure AD Tenant ID")
    parser.add_argument("--client-id", required=True, help="App Registration Client ID")
    parser.add_argument("--client-secret", required=True, help="App Registration Client Secret")
    parser.add_argument("--output", default="m365_license_report.csv", help="Output CSV file")

    args = parser.parse_args()

    print("🔐 Getting access token...")
    token = get_access_token(args.tenant_id, args.client_id, args.client_secret)

    print("📡 Fetching users and licenses from Microsoft Graph...")
    users = fetch_users_with_licenses(token)

    print(f"💾 Exporting report to {args.output}...")
    export_to_csv(users, args.output)

    print("✅ Done! License report generated successfully.")


if __name__ == "__main__":
    main()
