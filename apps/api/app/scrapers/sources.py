from dataclasses import dataclass


@dataclass
class ScrapedJob:
    source: str
    source_url: str
    title: str
    company: str
    location: str
    description: str


def scrape_greenhouse_jobs() -> list[ScrapedJob]:
    return []


def scrape_lever_jobs() -> list[ScrapedJob]:
    return []


def scrape_ashby_jobs() -> list[ScrapedJob]:
    return []


def scrape_yc_jobs() -> list[ScrapedJob]:
    return []
