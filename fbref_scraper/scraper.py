import logging

from fbref_scraper.config import BASE_URL, MAX_RETRIES, BACKOFF_FACTOR, COMPETITION_NAME_TO_ID
from fbref_scraper.models import SeasonFixtures, MatchSummary, MatchShots, MatchReport
from fbref_scraper.network.web_client import WebClient
from fbref_scraper.parsers import FixturesParser, MatchSummaryParser, ShotsParser


class FbRefScraper:
    def __init__(self):
        self.client = WebClient(max_retries=MAX_RETRIES, backoff_factor=BACKOFF_FACTOR)

    def download_fixtures(self, competition_name: str, season: str) -> dict:
        competition_id = self._get_competition_id(competition_name)
        url = f'{BASE_URL}/comps/{competition_id}/{season}/schedule/'
        html = self.client.get(url)
        fixtures = FixturesParser().parse(html)
        return SeasonFixtures(competition_id, competition_name, season, fixtures).to_dict()

    def download_match_report(self, match_id: str) -> dict:
        url = f'{BASE_URL}/matches/{match_id}/'
        html = self.client.get(url)
        summary = MatchSummaryParser().parse(html)
        if summary is None:
            logging.warning(f'No match summary found for match {match_id}')
        shots = ShotsParser().parse(html)
        if shots is None:
            logging.warning(f'No shots found for match {match_id}')
        return MatchReport(match_id, summary, shots).to_dict()

    def download_match_summary(self, match_id: str) -> dict:
        url = f'{BASE_URL}/matches/{match_id}/'
        html = self.client.get(url)
        summary = MatchSummaryParser().parse(html)
        if summary is None:
            logging.warning(f'No match summary found for match {match_id}')
        return MatchSummary(match_id, summary).to_dict()

    def download_match_shots(self, match_id: str) -> dict:
        url = f'{BASE_URL}/matches/{match_id}/'
        html = self.client.get(url)
        shots = ShotsParser().parse(html)
        if shots is None:
            logging.warning(f'No shots found for match {match_id}')
        return MatchShots(match_id, shots).to_dict()

    @staticmethod
    def _get_competition_id(competition_name: str) -> str:
        competition_id = COMPETITION_NAME_TO_ID.get(competition_name)
        if competition_id is None:
            raise Exception(f'Competition {competition_name} not supported! '
                            f'Supported competitions are: {list(COMPETITION_NAME_TO_ID.keys())}')
        return competition_id
