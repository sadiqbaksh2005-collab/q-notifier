import json
import os
import urllib.request
 
SRC = ("https://raw.githubusercontent.com/SimplifyJobs/"
       "Summer2027-Internships/dev/.github/scripts/listings.json")
STATE = "seen_ids.json"
TOPIC = os.environ["NTFY_TOPIC"]
TERM = "Summer 2027"
CATEGORIES = {"Quant", "Quantitative Finance"}
 
 
def fetch():
    with urllib.request.urlopen(SRC, timeout=60) as r:
        return json.load(r)
 
 
def current_quant(listings):
    return {
        x["id"]: x for x in listings
        if x.get("category") in CATEGORIES
        and x.get("active") and x.get("is_visible")
        and TERM in x.get("terms", [])
    }
 
 
def notify(job):
    locs = ", ".join(job.get("locations", [])[:3]) or "Location n/a"
    req = urllib.request.Request(
        f"https://ntfy.sh/{TOPIC}",
        data=f"{job['title']}\n{locs}".encode(),
        headers={
            "Title": f"New quant: {job['company_name']}",
            "Click": job["url"],
            "Tags": "chart_with_upwards_trend",
        },
    )
    urllib.request.urlopen(req, timeout=30)
 
 
def main():
    jobs = current_quant(fetch())
    first_run = not os.path.exists(STATE)
    seen = set() if first_run else set(json.load(open(STATE)))
 
    if not first_run:
        for job_id, job in jobs.items():
            if job_id not in seen:
                notify(job)
 
    # Cumulative: never forget an id, so a listing that flips inactive and
    # back to active (common with Goldman Sachs) is not announced twice.
    json.dump(sorted(seen | set(jobs)), open(STATE, "w"))
 
 
if __name__ == "__main__":
    main()
