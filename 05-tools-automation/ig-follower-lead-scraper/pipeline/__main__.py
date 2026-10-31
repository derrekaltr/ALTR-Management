import argparse

from .export import export, status
from .followers import scrape_followers
from .prefilter import prefilter
from .profiles import scrape_profiles
from .rubric import qualify


def main():
    p = argparse.ArgumentParser(prog="pipeline", description="IG follower lead-qualification pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, needs_spend in (
        ("scrape-followers", True),
        ("prefilter", False),
        ("scrape-profiles", True),
        ("qualify", False),
        ("export", False),
        ("status", False),
    ):
        sp = sub.add_parser(name)
        sp.add_argument("--target", required=True, help="Client IG handle whose followers we scrape")
        if needs_spend:
            sp.add_argument("--limit", type=int, default=None, help="Cap results (use a small value for the pilot)")
            sp.add_argument("--yes", action="store_true", help="Confirm paid Apify spend")
        if name == "export":
            sp.add_argument("--min-score", type=int, default=1, help="Only export leads at/above this score (1-5)")

    args = p.parse_args()
    target = args.target.lstrip("@").lower()
    if args.cmd == "scrape-followers":
        scrape_followers(target, limit=args.limit, yes=args.yes)
    elif args.cmd == "prefilter":
        prefilter(target)
    elif args.cmd == "scrape-profiles":
        scrape_profiles(target, limit=args.limit, yes=args.yes)
    elif args.cmd == "qualify":
        qualify(target)
    elif args.cmd == "export":
        export(target, min_score=args.min_score)
    elif args.cmd == "status":
        status(target)


if __name__ == "__main__":
    main()
