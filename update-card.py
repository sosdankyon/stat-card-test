import base64
import json
import tomllib
from typing import Final, Optional
from lxml import etree

import requests
from datetime import datetime
import os
import sys
from loguru import logger


def log_formatter(record):
    short_level = record["level"].name[0]
    color = {"D": "blue", "I": "black", "W": "yellow", "E": "red"}
    color = color.get(short_level, "black")
    return "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>" + short_level + "</level>] - <" + color + ">{message}</" + color + ">\n"


class StatUpdater:
    def __init__(self):
        logger.remove()
        logger.add(sys.stdout, colorize=True, format=log_formatter, level="DEBUG")

        with open("config.toml", "rb") as f:
            self.CONFIG = tomllib.load(f)
        print(json.dumps(self.CONFIG, indent=4))

        self.TOKEN: Final[Optional[str]] = os.getenv("TOKEN", default=None)
        self.USER_NAME: Final[Optional[str]] = os.getenv("USER_NAME", default=None)
        self.FONT: Optional[str] = os.getenv("FONT", default=None)

        if self.TOKEN is None:
            raise Exception("TOKEN not set")
        if self.USER_NAME is None:
            raise Exception("USER_NAME not set")
        if self.FONT is None:
            self.FONT = "assets/DungGeunMo_ascii.woff2"
            logger.info(f"use default font: {self.FONT}")

    def update(self):
        stats = self.fetch()
        b64_font = self.get_font()
        self.make_card(stats, b64_font)

    def fetch(self):
        logger.info(f"Get repository list...")
        repos = self.request_api("/user/repos?affiliation=owner", get_all_pages=True)
        collabo_repos = self.request_api("/user/repos?affiliation=collaborator", get_all_pages=True)
        total_repo_count = len(repos) + len(collabo_repos)
        logger.info(f"Get {total_repo_count} repositories")

        total_star = 0
        total_fork = 0
        public_repo_count = 0
        private_repo_count = 0
        for repo in repos:
            total_star += repo["stargazers_count"]
            total_fork += repo["forks_count"]
            if repo["private"]:
                private_repo_count += 1
            else:
                public_repo_count += 1
        logger.info(f"You have {public_repo_count} public, {private_repo_count} private repositories")
        logger.info(f"You have {total_star} stars, {total_fork} forks")

        user_info = self.request_api(f"/users/{self.USER_NAME}")
        total_followers = user_info["followers"]
        logger.info(f"You have {total_followers} followers")

        commit_count = self.get_search_count("commits", f"author:{self.USER_NAME}")
        logger.info(f"You have {commit_count} commits")

        now = datetime.now()
        year = now.year
        commit_count_this_year = self.get_search_count("commits", f"author:{self.USER_NAME} author-date:{year}-01-01..{year}-12-31")
        logger.info(f"You have {commit_count_this_year} commits this year")

        issue_count = self.get_search_count("issues", f"author:{self.USER_NAME} is:issue")
        pr_count = self.get_search_count("issues", f"author:{self.USER_NAME} is:pr")
        logger.info(f"You made {issue_count} issues, {pr_count} PRs")

        return {
            "repo_pub": public_repo_count,
            "repo_pri": private_repo_count,
            "repo_col": len(collabo_repos),
            "star": total_star,
            "fork": total_fork,
            "followers": total_followers,
            "commits": commit_count,
            "commits_this_year": commit_count_this_year,
            "this_year": year,
            "issue": issue_count,
            "pr": pr_count,
            "now": now.strftime(self.CONFIG["date"]["date_format"]),
        }

    def get_font(self) -> str:
        if self.FONT.startswith("https://"):
            logger.info(f"Get font from url {self.FONT}")
            response = requests.get(self.FONT)
            response.raise_for_status()
            logger.info(f"font size: {len(response.content)}")
            return base64.b64encode(response.content).decode("utf-8")
        else:
            logger.info(f"Get font from path {self.FONT}")
            with open(self.FONT, "rb") as f:
                data = f.read()
                logger.info(f"font size: {len(data)}")
                return base64.b64encode(data).decode("utf-8")

    def make_card(self, stats: dict, b64_font: str):
        card = ""
        with open("assets/template.svg", "r", encoding="utf-8") as f:
            card = f.read()

        root = etree.fromstring(card)
        ns = {"svg": "http://www.w3.org/2000/svg"}
        root.xpath(".//*[@id='user-name']", namespaces=ns)[0].text = self.USER_NAME
        root.xpath(".//*[@id='update-date']", namespaces=ns)[0].text = stats["now"] + " UTC"

        root.xpath(".//*[@id='style-font-face']", namespaces=ns)[0].text = f"""
@font-face {{
  font-family: 'Font';
  src: url(data:font/woff2;charset=utf-8;base64,{b64_font}) format('woff2');
  font-weight: normal;
  font-display: block;
}}"""

        display_total_repo_count = 0
        if self.CONFIG["repo"]["show_mode"] == "total":
            display_total_repo_count = stats["repo_pub"] + stats["repo_pri"] + stats["repo_col"]
            root.xpath(".//*[@id='text-repo-total']", namespaces=ns)[0].text = "Total"
            root.xpath(".//*[@id='repo-total']", namespaces=ns)[0].text = str(display_total_repo_count)
        elif self.CONFIG["repo"]["show_mode"] == "detail":
            if not self.CONFIG["repo"]["include_public_repos"] and not self.CONFIG["repo"]["include_private_repos"] and not self.CONFIG["repo"]["include_collaborator_repo"]:
                raise Exception("At least one type of repository must be displayed")
            if self.CONFIG["repo"]["include_public_repos"]:
                display_total_repo_count += stats["repo_pub"]
                root.xpath(".//*[@id='repo-pub']", namespaces=ns)[0].text = str(stats["repo_pub"])
                root.xpath(".//*[@id='text-repo-pub']", namespaces=ns)[0].text = "public"
            if self.CONFIG["repo"]["include_private_repos"]:
                display_total_repo_count += stats["repo_pri"]
                root.xpath(".//*[@id='repo-pri']", namespaces=ns)[0].text = str(stats["repo_pri"])
                root.xpath(".//*[@id='text-repo-pri']", namespaces=ns)[0].text = "private"
            if self.CONFIG["repo"]["include_collaborator_repo"]:
                display_total_repo_count += stats["repo_col"]
                root.xpath(".//*[@id='repo-col']", namespaces=ns)[0].text = str(stats["repo_col"])
                root.xpath(".//*[@id='text-repo-col']", namespaces=ns)[0].text = "collabo"
        else:
            raise Exception("config repo.show_mode is wrong")

        root.xpath(".//*[@id='text-repository']", namespaces=ns)[0].text = "repositories" if display_total_repo_count > 1 else "repository"

        root.xpath(".//*[@id='commit']", namespaces=ns)[0].text = str(stats["commits"])
        root.xpath(".//*[@id='text-commit-0']", namespaces=ns)[0].text = " total commits"
        if self.CONFIG["commit"]["show_commit_this_year"]:
            root.xpath(".//*[@id='text-commit-0']", namespaces=ns)[0].text += "("
            root.xpath(".//*[@id='commit-year']", namespaces=ns)[0].text = str(stats["commits_this_year"])
            root.xpath(".//*[@id='text-commit-1']", namespaces=ns)[0].text = " this year)"
        else:
            root.xpath(".//*[@id='commit-year']", namespaces=ns)[0].text = ""
            root.xpath(".//*[@id='text-commit-1']", namespaces=ns)[0].text = ""

        root.xpath(".//*[@id='text-star-0']", namespaces=ns)[0].text = "Earned"
        root.xpath(".//*[@id='star']", namespaces=ns)[0].text = str(stats["star"])
        root.xpath(".//*[@id='text-star-1']", namespaces=ns)[0].text = "stars"

        root.xpath(".//*[@id='text-fork-0']", namespaces=ns)[0].text = "Forked"
        root.xpath(".//*[@id='fork']", namespaces=ns)[0].text = str(stats["fork"])
        root.xpath(".//*[@id='text-fork-1']", namespaces=ns)[0].text = "times"

        root.xpath(".//*[@id='text-pr-0']", namespaces=ns)[0].text = "Opened"
        root.xpath(".//*[@id='pr']", namespaces=ns)[0].text = str(stats["pr"])
        root.xpath(".//*[@id='text-pr-1']", namespaces=ns)[0].text = "PRs"

        root.xpath(".//*[@id='text-issue-0']", namespaces=ns)[0].text = "Opened"
        root.xpath(".//*[@id='issue']", namespaces=ns)[0].text = str(stats["issue"])
        root.xpath(".//*[@id='text-issue-1']", namespaces=ns)[0].text = "Issues"

        with open("my-github-stats.svg", "w", encoding="utf-8") as f:
            f.write(etree.tostring(root, encoding="unicode"))

    def request_api(self, endpoint: str, get_all_pages: bool = False) -> list | dict:
        headers = {"Authorization": f"token {self.TOKEN}"}

        url = f"https://api.github.com" + endpoint
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result: list = response.json()

        if get_all_pages and response.links.get("next"):
            while response.links.get("next") is not None:
                response = requests.get(response.links["next"]["url"], headers=headers)
                response.raise_for_status()
                result.extend(response.json())

        return result

    def get_search_count(self, endpoint: str, q: str) -> int:
        headers = {"Authorization": f"token {self.TOKEN}"}

        url = f"https://api.github.com/search/{endpoint}"
        response = requests.get(url, headers=headers, params={"q": q})
        response.raise_for_status()
        result: dict = response.json()

        return result["total_count"]


if __name__ == "__main__":
    StatUpdater().update()
