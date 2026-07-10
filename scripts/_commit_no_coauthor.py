import os
import subprocess
import sys
import tempfile


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/_commit_no_coauthor.py <commit message>")

    tree = subprocess.check_output(["git", "write-tree"], text=True).strip()
    parent = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    msg = sys.argv[1].rstrip("\n") + "\n"
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as handle:
        handle.write(msg)
        msg_path = handle.name

    env = os.environ.copy()
    for key, fmt in [
        ("GIT_AUTHOR_NAME", "%an"),
        ("GIT_AUTHOR_EMAIL", "%ae"),
        ("GIT_COMMITTER_NAME", "%cn"),
        ("GIT_COMMITTER_EMAIL", "%ce"),
    ]:
        env[key] = subprocess.check_output(
            ["git", "log", "-1", f"--format={fmt}"], text=True
        ).strip()

    new_commit = subprocess.check_output(
        ["git", "commit-tree", tree, "-p", parent, "-F", msg_path],
        env=env,
        text=True,
    ).strip()
    subprocess.check_call(["git", "update-ref", "HEAD", new_commit])
    subprocess.check_call(["git", "reset", "--mixed", "HEAD"])
    print(subprocess.check_output(["git", "log", "-1", "--format=%H%n%s%n%b"], text=True))


if __name__ == "__main__":
    main()
