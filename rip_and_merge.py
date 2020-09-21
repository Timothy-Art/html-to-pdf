import os
import click
from driver.utils import get_driver
from rip import PageRipper
from merge import PageMerger


@click.command()
@click.argument('site')
@click.argument('title')
@click.option('--driver', type=click.Choice(['chrome', 'firefox'], case_sensitive=False),
              default='chrome')
@click.option('--directory', type=click.Path(dir_okay=True), default='.')
@click.option('--headless/--not-headless', default=True)
@click.option('--output', default='output.pdf')
@click.option('--username', prompt='OWL Username?')
@click.option('--password', prompt='Password?', hide_input=True)
def main(username, password, driver, site, title, directory, headless, output):
    driver, options = get_driver(driver, headless)

    if os.path.isdir(directory):
        os.mkdir(directory)

    PageRipper(
        driver=driver,
        user=username,
        password=password,
        site=site,
        title=title
    ).run(options=options, directory=directory)
    PageMerger.run(directory, output)


if __name__ == '__main__':
    main()
