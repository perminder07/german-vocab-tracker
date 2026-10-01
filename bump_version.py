import sys
import re

def bump_version(bump_type="patch"):
    # 1. Read current version
    try:
        with open("version.txt", "r") as f:
            current = f.read().strip()
    except FileNotFoundError:
        current = "1.0.0"

    major, minor, patch = map(int, current.split("."))
    
    # 2. Apply Semantic Versioning logic
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
        
    new_version = f"{major}.{minor}.{patch}"
    
    # 3. Update version.txt
    with open("version.txt", "w") as f:
        f.write(new_version)
        
    # 4. Update README.md badge (matches "badge/version-X.X.X")
    with open("README.md", "r") as f:
        readme = f.read()
    readme = re.sub(r"badge/version-\d+\.\d+\.\d+", f"badge/version-{new_version}", readme)
    with open("README.md", "w") as f:
        f.write(readme)
        
    # 5. Update index.html header (matches "vX.X.X")
    with open("index.html", "r") as f:
        html = f.read()
    html = re.sub(r"v\d+\.\d+\.\d+", f"v{new_version}", html)
    with open("index.html", "w") as f:
        f.write(html)
        
    print(f"Successfully bumped version: {current} -> {new_version}")

if __name__ == "__main__":
    # Defaults to 'patch' if no argument is provided
    bump_type = sys.argv[1].lower() if len(sys.argv) > 1 else "patch"
    bump_version(bump_type)