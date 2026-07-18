#!/usr/bin/env python3
"""
Fetches public LeetCode solve stats via LeetCode's own GraphQL endpoint --
no login, no API key, same no-auth trick as fetch_contributions.py uses
for GitHub. Writes data/leetcode.json.

NOTE: this could not be tested in the sandbox that generated it --
leetcode.com isn't on that environment's network allowlist. Run this
locally FIRST and confirm it prints real numbers before wiring it into
the GitHub Actions workflow. If LeetCode has changed their schema or
added stricter bot-blocking since this was written, the request may
need a User-Agent header tweak or may fail outright -- if so, paste me
the exact error and we'll adjust.
"""
import json
import os
import urllib.request

USERNAME = os.environ.get("LEETCODE_USER", "Z_lmaoooo")
HERE = os.path.dirname(__file__)
OUT_PATH = os.path.join(HERE, "..", "data", "leetcode.json")

QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStatsGlobal {
      acSubmissionNum { difficulty count }
    }
  }
}
"""


def fetch(username):
    body = json.dumps({"query": QUERY, "variables": {"username": username}}).encode()
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (profile-readme-script)",
            "Referer": f"https://leetcode.com/u/{username}/",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


if __name__ == "__main__":
    raw = fetch(USERNAME)
    user = raw.get("data", {}).get("matchedUser")
    if not user:
        raise SystemExit(f"No such LeetCode user, or LeetCode blocked the request. Raw response: {raw}")

    counts = {row["difficulty"]: row["count"] for row in user["submitStatsGlobal"]["acSubmissionNum"]}
    result = {
        "username": user["username"],
        "total_solved": counts.get("All", 0),
        "easy": counts.get("Easy", 0),
        "medium": counts.get("Medium", 0),
        "hard": counts.get("Hard", 0),
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"wrote {OUT_PATH}: {result['total_solved']} solved "
          f"({result['easy']} easy / {result['medium']} medium / {result['hard']} hard)")