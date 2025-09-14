import subprocess

print("Final commit - cleaning up...")
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Clean up temporary files"])
subprocess.run(["git", "push", "origin", "master"])
print("Done!")
