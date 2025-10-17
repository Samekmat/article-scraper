from django.core.management.base import BaseCommand

from articles.scraper import scrape_article_selenium


class Command(BaseCommand):
    help = (
        "Scrape articles from provided URLs. "
        "You can pass URLs as positional arguments or with --urls. "
        "If no URLs are provided, the command scrapes 4 predefined task URLs."
    )

    def add_arguments(self, parser):
        # Positional URLs (optional)
        parser.add_argument(
            "input_urls",
            nargs="*",
            type=str,
            help="Optional positional URLs to scrape (space-separated).",
        )
        # Optional flag --urls URL1 URL2 ...
        parser.add_argument(
            "--urls",
            nargs="+",
            type=str,
            help="Optional list of URLs to scrape (space-separated).",
        )

    def handle(self, *args, **options):
        default_urls = [
            "https://galicjaexpress.pl/ford-c-max-jaki-silnik-benzynowy-wybrac-aby-zaoszczedzic-na-paliwie",
            "https://galicjaexpress.pl/bmw-e9-30-cs-szczegolowe-informacje-o-osiagach-i-historii-modelu",
            "https://take-group.github.io/example-blog-without-ssr/jak-kroic-piers-z-kurczaka-aby-uniknac-suchych-kawalkow-miesa",
            "https://take-group.github.io/example-blog-without-ssr/co-mozna-zrobic-ze-schabu-oprocz-kotletow-5-zaskakujacych-przepisow",
        ]
        provided_urls = options.get("urls") or options.get("input_urls")
        urls = provided_urls if provided_urls else default_urls
        if not provided_urls:
            self.stdout.write(
                self.style.NOTICE if hasattr(self.style, "NOTICE") else str
            )("No URLs provided. Using 4 predefined task URLs.")
        total = len(urls)

        for idx, url in enumerate(urls, start=1):
            self.stdout.write(f"Scraping article {idx} / {total}: {url}")
            article = scrape_article_selenium(url)
            if article:
                self.stdout.write(self.style.SUCCESS(f"Saved: {article.title}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Already exists or failed: {url}")
                )

        self.stdout.write(self.style.SUCCESS("Scraping finished!"))
