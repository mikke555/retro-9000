import questionary

import settings
from models.submission import Submission
from modules.avax import Avax
from modules.config import logger
from modules.utils import divide_amounts_evenly, random_sleep, read_txt, sleep


def get_user_input() -> list[Submission]:
    submissions = Avax.fetch_submissions("submissions.json")
    project_names = [project.name for project in submissions]

    user_projects = questionary.checkbox(
        "Select project to vote for:",
        choices=project_names,
    ).ask()

    if not user_projects:
        exit(0)

    return [
        submission for submission in submissions if submission.name in user_projects
    ]


def main():
    keys, proxies = read_txt("keys.txt", "proxies.txt")
    projects = get_user_input()

    for index, key in enumerate(keys, start=1):
        try:
            label = f"[{index}/{len(keys)}]"

            avax = Avax(
                private_key=key,
                label=label,
                proxy=proxies[index - 1],
            )

            voting_power = avax.login()
            if not voting_power:
                continue

            votes_per_project = divide_amounts_evenly(voting_power, len(projects))

            for i, project in enumerate(projects):
                random_vote = votes_per_project[i]
                avax.vote(project, random_vote)
                random_sleep(2, 10)

            avax.confirm_votes()

            if index < len(keys):
                sleep(*settings.SLEEP_BETWEEN_WALLETS)

        except Exception as error:
            logger.error(f"{label} Error processing wallet: {error} \n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Cancelled by user")
