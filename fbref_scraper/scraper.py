import logging

from .config import BASE_URL, competition_name_to_id, MAX_RETRIES, BACKOFF_FACTOR
from .network.web_client import WebClient
from .parsers import FixturesParser, MatchSummaryParser, ShotsParser


class FbRefScraper:
    def __init__(self):
        self.client = WebClient(max_retries=MAX_RETRIES, backoff_factor=BACKOFF_FACTOR)

    def download_fixtures(self, competition_name: str, season: str) -> dict:
        competition_id = self._get_competition_id(competition_name)
        url = f'{BASE_URL}/comps/{competition_id}/{season}/schedule/'
        html = self.client.get(url)
        fixtures = FixturesParser().parse(html)
        return {
            'competition_id': competition_id,
            'competition_name': competition_name,
            'season': season,
            'fixtures': fixtures
        }

    def download_match_report(self, match_id: str) -> dict:
        url = f'{BASE_URL}/matches/{match_id}/'
        html = self.client.get(url)
        summary = MatchSummaryParser().parse(html)
        if summary is None:
            logging.warning(f'No match summary found for match {match_id}')
        shots = ShotsParser().parse(html)
        if shots is None:
            logging.warning(f'No shots found for match {match_id}')
        return {
            'match_id': match_id,
            'match_summary': summary,
            'shots': shots
        }

    def download_match_summary(self, match_id: str) -> dict:
        url = f'{BASE_URL}/matches/{match_id}/'
        html = self.client.get(url)
        summary = MatchSummaryParser().parse(html)
        if summary is None:
            logging.warning(f'No match summary found for match {match_id}')
        return {
            'match_id': match_id,
            'summary': summary
        }

    def download_match_shots(self, match_id: str) -> dict:
        url = f'{BASE_URL}/matches/{match_id}/'
        html = self.client.get(url)
        shots = ShotsParser().parse(html)
        if shots is None:
            logging.warning(f'No shots found for match {match_id}')
        return {
            'match_id': match_id,
            'shots': shots
        }

    @staticmethod
    def _get_competition_id(competition_name: str) -> str:
        competition_id = competition_name_to_id.get(competition_name)
        if competition_id is None:
            raise Exception(f'Competition {competition_name} not supported! '
                            f'Supported competitions are: {list(competition_name_to_id.keys())}')
        return competition_id
