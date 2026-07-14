"""
Demonstrates how to download a file from SharePoint site
"""

import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

test_client_id = "8c59ead7-d703-4a27-9e55-c96a0054c8d2"
test_client_secret = ""
test_site_url = "https://maitgroup-my.sharepoint.com/personal/noel_weiss_mait-group_com"
test_tenant = "noel.weiss@mait-group.com"

ctx = ClientContext(test_site_url).with_interactive(test_tenant, client_id=test_client_id)

file_url = "Documents/Noncompliant_Settings_by_User.xlsx"
# file_url = "Shared Documents/big_buck_bunny.mp4"
# file_url = "Shared Documents/Financial Sample.xlsx"
# file_url = "Shared Documents/report '123.csv"
download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
with open(download_path, "wb") as local_file:
    file = ctx.web.get_file_by_server_relative_path(file_url).download(local_file).execute_query()
    print(f"[Ok] file has been downloaded into: {download_path}")