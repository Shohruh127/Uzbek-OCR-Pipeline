# Vendor Directory

Place vendored Python wheel (.whl) files here for air-gapped deployment.

Download wheels on a connected machine:
```bash
pip download -r requirements.txt -d vendor/
```

Then build the Docker image with `--network=none`.
