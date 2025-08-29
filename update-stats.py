import base64
from typing import Final, Optional

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
        self.TOKEN: Final[Optional[str]] = os.getenv("TOKEN", default=None)
        self.USER_NAME: Final[Optional[str]] = os.getenv("USER_NAME", default=None)
        self.FONT: Optional[str] = os.getenv("FONT", default=None)

        if self.TOKEN is None:
            raise Exception("TOKEN not set")
        if self.USER_NAME is None:
            raise Exception("USER_NAME not set")
        if self.FONT is None:
            raise Exception("FONT not set")

        logger.remove()
        logger.add(sys.stdout, colorize=True, format=log_formatter, level="DEBUG")

    def update(self):
        stats = self.fetch()
        b64_font = self.get_font()
        self.make_card(stats, b64_font)

    def fetch(self):
        logger.info(f"Get repository list...")
        repos = self.request_api("/user/repos?affiliation=owner", get_all_pages=True)
        total_repo_count = len(repos)
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
            "star": total_star,
            "fork": total_fork,
            "followers": total_followers,
            "commits": commit_count,
            "commits_this_year": commit_count_this_year,
            "this_year": year,
            "issue": issue_count,
            "pr": pr_count,
            "now": now.strftime("%Y-%m-%d %H:%M"),
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
        with open("template.svg", "r", encoding="utf-8") as f:
            card = f.read()

        card = (card.replace("{REPO_PUB}", str(stats["repo_pub"]))
                .replace("{REPO_PRI}", str(stats["repo_pri"]))
                .replace("{STAR}", str(stats["star"]))
                .replace("{FORK}", str(stats["fork"]))
                .replace("{COMMIT_TOTAL}", str(stats["commits"]))
                .replace("{COMMIT_THIS_YEAR}", str(stats["commits_this_year"]))
                .replace("{PR}", str(stats["pr"]))
                .replace("{ISSUE}", str(stats["issue"]))
                .replace("{UPDATE_DATE}", stats["now"])
                .replace("{USER_NAME}", self.USER_NAME)
                .replace("{B64_FONT}", b64_font))

        with open("result.svg", "w", encoding="utf-8") as f:
            f.write(card)

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
