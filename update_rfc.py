import os
path = r'c:\app\neevaiplatform-backend\rfc.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_val = '''### Image Validation
When a user attempts to launch a BYOI sandbox, the platform performs a lightweight compatibility check to prevent immediate crashes:
*   Verifies the presence of a compatible OS release (`/etc/os-release`).
*   Verifies a valid shell exists (`/bin/sh`).
If these checks fail, the sandbox creation is aborted and the user is provided with a clear error message.'''

new_val = '''### Image Validation
When a user attempts to launch a BYOI sandbox, the platform performs a lightweight compatibility check to prevent immediate crashes and ensure quota compliance:
*   **Size Validation**: The platform inspects the OCI Image Manifest to calculate the total uncompressed size of the image layers. If the total size exceeds the disk limit of the user's selected compute tier, sandbox creation is aborted instantly with an "Image Too Large" error.
*   **Runtime Validation**: Verifies the presence of a compatible OS release (`/etc/os-release`).
*   **Shell Validation**: Verifies a valid shell exists (`/bin/sh`).
If any of these checks fail, the sandbox creation is aborted and the user is provided with a clear, actionable error message rather than experiencing a frustrating runtime crash.'''

content = content.replace(old_val, new_val)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully updated Image Validation section.')
