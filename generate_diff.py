import subprocess

def get_full_git_diff(source_branch, target_branch):
    """Get the full git diff between source and target branches"""
    try:
        cmd = [
            "git", "diff", f"origin/{target_branch}",
            f"origin/{source_branch}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting full git diff: {e}")
        print(f"stderr: {e.stderr}")
        return ""


def get_commit_ids(source_branch, target_branch):
    """Get commit IDs for source and target branches"""
    try:
        # Get source branch commit
        cmd_source = ["git", "rev-parse", f"origin/{source_branch}"]
        result_source = subprocess.run(cmd_source, capture_output=True, text=True, check=True)
        source_commit = result_source.stdout.strip()
        
        # Get target branch commit
        cmd_target = ["git", "rev-parse", f"origin/{target_branch}"]
        result_target = subprocess.run(cmd_target, capture_output=True, text=True, check=True)
        target_commit = result_target.stdout.strip()
        
        # Return as comma-separated string: "source_commit,target_commit"
        return f"{source_commit},{target_commit}"
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit IDs: {e}")
        print(f"stderr: {e.stderr}")
        return ""