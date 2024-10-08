import logging
from typing import Optional, List

import bs4

from fbref_scraper.parsers.base import BaseParser
from fbref_scraper.parsers.utils import get_period_and_minute, get_entity_id_and_name
from fbref_scraper.models import SummaryEvent


class MatchSummaryParser(BaseParser):
    def parse(self, html: str) -> Optional[List[SummaryEvent]]:
        soup = bs4.BeautifulSoup(html, 'html.parser')
        raw_events = self._get_raw_events(soup)
        if raw_events is None:
            return None
        parsed_events = []
        for event in raw_events:
            try:
                parsed_events.append(self._parse_event(event))
            except Exception as e:
                logging.error(f'Error while parsing summary event {event}: {e}')
        valid_events = [event for event in parsed_events if event is not None]
        return valid_events

    def _parse_event(self, event) -> Optional[SummaryEvent]:
        period, minute = self._get_event_period_and_minute(event)
        event_type = self._get_event_type(event)
        team_id = self._get_team_id(event)
        player_id, player_name = self._get_player_info(event)
        if player_id is None:
            return None
        return SummaryEvent(team_id, player_id, player_name, event_type, period, minute)

    @staticmethod
    def _get_raw_events(soup: bs4.BeautifulSoup) -> Optional[bs4.element.ResultSet]:
        match_summary = soup.find('div', {'id': 'events_wrap'})
        if match_summary is None:
            return None
        return match_summary.find_all('div', class_='event')

    @staticmethod
    def _get_event_type(event: bs4.element.Tag) -> str:
        return event.find('div', class_='event_icon')['class'][1]

    @staticmethod
    def _get_team_id(event: bs4.element.Tag) -> str:
        return event.find('img')['src'].split('/')[-1].split('.')[0]

    @staticmethod
    def _get_event_period_and_minute(event: bs4.element.Tag) -> tuple[str, int]:
        minute_string = event.find('div').text.split('\n')[1].replace('\t', '').replace('\xa0', '').replace('’', '')
        return get_period_and_minute(minute_string)

    @staticmethod
    def _get_player_info(event: bs4.element.Tag) -> tuple[Optional[str], Optional[str]]:
        player = event.find('a')
        if player is None:
            return None, None
        return get_entity_id_and_name(player)
