from django.core.management.base import BaseCommand
from articles.scraper import scrape_article_selenium


class Command(BaseCommand):
    help = 'Scrapes articles from the given urls. Use --urls for custom URLs, else scrapes default batch.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--urls',
            nargs='+',
            type=str,
            help='Optional list of URLs to scrape, separated by space.'
        )

    def handle(self, *args, **options):
        default_urls = [
            "https://galicjaexpress.pl/ford-c-max-jaki-silnik-benzynowy-wybrac-aby-zaoszczedzic-na-paliwie",
            "https://galicjaexpress.pl/bmw-e9-30-cs-szczegolowe-informacje-o-osiagach-i-historii-modelu",
            "https://take-group.github.io/example-blog-without-ssr/jak-kroic-piers-z-kurczaka-aby-uniknac-suchych-kawalkow-miesa",
            "https://take-group.github.io/example-blog-without-ssr/co-mozna-zrobic-ze-schabu-oprocz-kotletow-5-zaskakujacych-przepisow",
        ]
        urls = options['urls'] if options['urls'] else default_urls
        total = len(urls)

        for idx, url in enumerate(urls, start=1):
            self.stdout.write(f"Scraping article {idx} / {total}: {url}")
            article = scrape_article_selenium(url)
            if article:
                self.stdout.write(self.style.SUCCESS(f"Saved: {article.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {url}"))

        self.stdout.write(self.style.SUCCESS("Scraping finished!"))