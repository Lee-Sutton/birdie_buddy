import os
from invoke import task
import site


@task
def tailwind(c, watch=True):
    """Configure PYSITE_PACKAGES and start Tailwind CSS"""
    # Get the site-packages directory
    site_packages = site.getsitepackages()[0]

    # Set environment variable
    os.environ["PYSITE_PACKAGES"] = site_packages

    # Build command based on watch flag
    cmd = "tailwindcss -i ./src/birdie_buddy/static/css/input.css -o ./src/birdie_buddy/static/css/output.css"
    if watch:
        cmd += " --watch"

    # Run tailwind
    c.run(cmd)
