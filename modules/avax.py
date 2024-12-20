import json
import os

from loguru import logger

from lib.http import HttpClient
from lib.wallet import Wallet
from models.submission import Submission


class Avax(Wallet):
    round_id = "cm3tfqk550005irarqtv047hz"

    def __init__(self, private_key, label, proxy):
        super().__init__(private_key, label, proxy)
        self.label += "Retro 9000 |"

    @classmethod
    def fetch_submissions(self, json_path="submissions.json"):
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                return [Submission(**submission) for submission in json.load(f)]

        client = HttpClient(proxy=None)
        url = f"https://api-retro-9000.avax.network/api/rounds/{self.round_id}/submissions"
        params = {
            "roundId": self.round_id,
            "page": "1",
            "perPage": "15",
            "sortBy": "votes",
            "sortOrder": "desc",
            "includeField": "userVotes",
        }

        r = client.get(url, params=params)
        data = r.json()["data"]

        with open(json_path, "w") as file:
            json.dump(data, file, indent=4)

        logger.success(f"Fetched data into {json_path}\n")
        return [Submission(**submission) for submission in data]

    def get_nonce(self):
        url = f"https://api-retro-9000.avax.network/api/auth/get-nonce/{self.address}"

        r = self.get(url)
        return r.json()["data"]["nonce"]

    def login(self):
        url = f"https://api-retro-9000.avax.network/api/auth/login"

        nonce = self.get_nonce()
        payload = {"walletAddress": self.address, "signature": self.sign_message(nonce)}

        r = self.post(url, json=payload)

        if r.status_code == 201:
            data = r.json()["data"]

            logger.debug(
                f"{self.label} Chill factor: {data['user']['chill_factor']}, Ref: {data['user']['referral_code']}, Referral Pts: {data['totalReferralPoints']}"
            )

            return data["user"]["chill_factor"]

    def vote(self, project: Submission, vote_count: int):
        url = f"https://api-retro-9000.avax.network/api/vote/rounds/{self.round_id}/projects/{project.id}/vote"

        r = self.post(url, json={"voteCount": vote_count})

        if r.json()["statusCode"] == 200:
            logger.info(
                f"{self.label} Voted for {project.name.strip()} with {vote_count} votes."
            )

    def get_vote_ids(self):
        url = f"https://api-retro-9000.avax.network/api/vote/rounds/{self.round_id}/ballot-votes"

        r = self.get(url)
        return r.json()["data"]["votes"]

    def confirm_votes(self):
        url = f"https://api-retro-9000.avax.network/api/vote/rounds/{self.round_id}/confirm-votes"
        vote_ids = [vote["id"] for vote in self.get_vote_ids()]

        payload = {"votes": []}
        for id in vote_ids:
            payload["votes"].append({"voteId": id})

        r = self.post(url, json=payload)
        data = r.json()

        if data["statusCode"] == 200:
            logger.success(f"{self.label} {data['message']}\n")
            return True
        else:
            logger.warning(f"{self.label} {data['message']}\n")
            return False
