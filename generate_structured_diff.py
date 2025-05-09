#!/usr/bin/env python3

import os
import sys
import json
import subprocess


def get_file_diff(file_path, source_branch, target_branch):
    """Get the diff for a specific file"""
    try:
        cmd = [
            "git", "diff", f"origin/{target_branch}",
            f"origin/{source_branch}", "--", file_path
        ]
        result = subprocess.run(cmd,
                                capture_output=True,
                                text=True,
                                check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff for {file_path}: {e}")
        print(f"stderr: {e.stderr}")
        return ""


def get_file_content(file_path, branch):
    """Get the content of a file at a specific branch"""
    try:
        cmd = ["git", "show", f"origin/{branch}:{file_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        return None  # File doesn't exist on this branch
    except Exception as e:
        print(f"Error getting content for {file_path} on {branch}: {e}")
        return None


def parse_changed_files(file_path):
    """Parse the file containing changed files info"""
    changes = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0]
                    file_path = parts[1]
                    changes.append({'status': status, 'file': file_path})
    except Exception as e:
        print(f"Error parsing changed files: {e}")

    return changes


def main():
    source_branch = os.environ.get('SOURCE_BRANCH')
    target_branch = os.environ.get('TARGET_BRANCH')

    if not all([source_branch, target_branch]):
        print("Missing required environment variables")
        sys.exit(1)

    # Parse changed files from the file
    changes = parse_changed_files('changed_files.txt')

    if not changes:
        print("No changed files found")
        sys.exit(1)

    print(f"Found {len(changes)} changed files")

    structured_diff = {"files": []}

    # Process each changed file
    for change in changes:
        if not change.get('file'):
            continue

        file_path = change.get('file')
        status = change.get('status', '?')

        # Map git status codes to more readable format
        status_map = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
        }

        file_status = status_map.get(status[0], 'unknown')

        file_diff = get_file_diff(file_path, source_branch, target_branch)

        # Get file content before and after
        before_content = get_file_content(
            file_path, target_branch) if file_status != 'added' else None
        after_content = get_file_content(
            file_path, source_branch) if file_status != 'deleted' else None

        # Create structured file information
        file_info = {
            "file_path": file_path,
            "status": file_status,
            "diff": file_diff,
            "extension": os.path.splitext(file_path)[1].lstrip('.'),
        }

        # Only include content if it's not too large
        if before_content and len(before_content) < 100000:  # 100KB limit
            file_info["before_content"] = before_content
        if after_content and len(after_content) < 100000:  # 100KB limit
            file_info["after_content"] = after_content

        structured_diff["files"].append(file_info)

    # Save structured diff to file
    with open('structured_diff.json', 'w', encoding='utf-8') as f:
        json.dump(structured_diff, f, indent=2)

    print(
        f"Generated structured diff with {len(structured_diff['files'])} files"
    )


if __name__ == "__main__":
    main()
