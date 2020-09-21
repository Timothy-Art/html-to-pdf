import click
import os
import re
from progress.bar import ChargingBar
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from driver.utils import get_driver


# From selenium docs.
class element_has_css_class(object):
    """
    An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """
    def __init__(self, locator, css_class):
        self.locator = locator
        self.css_class = css_class

    def __call__(self, driver):
        element = driver.find_element(*self.locator)   # Finding the referenced element
        if self.css_class in element.get_attribute("class"):
            return element
        else:
            return False


class ImageEmbedder:
    image_finder = re.compile(r'<img.*?>')
    watermark = re.compile(r'<div class="watermark">.*?</div>')
    image_sub = '<img src="data:image/png;base64, %s">'

    def embed_images(self, session):
        """
        Embeds images and cleans out watermarks from an active selenium session.

        :param session: Selenium Driver.
        :return: HTML string
        """
        content = session.page_source
        images = session.find_elements_by_tag_name('img')
        matches = self.image_finder.findall(content)

        for image, match in zip(images, matches):
            encoded_image = image.screenshot_as_base64
            content = content.replace(match, self.image_sub % encoded_image, 1)

        content = self.watermark.sub('', content)
        return content


class PageRipper:
    auth_site = 'https://owl.uwo.ca/portal'
    embedder = ImageEmbedder()

    def __init__(self, driver, user, password, site, title):
        """
        Rips a sequence of pages driven by Selenium and exports them to an output directory.

        :param driver: Driver to use.
        :param user: Username to login with.
        :param password: Password to login with.
        :param site: Site to attempt to rip.
        :param title: Name of document to rip.
        """
        self.driver = driver
        self.user = user
        self.password = password
        self.target = site
        self.title = title
        self.pages = None

    @staticmethod
    def wait_for_page(session):
        """
        Waits for the e-pub container to become visible.
        """
        WebDriverWait(session, 10).until(
            element_has_css_class((By.ID, 'epub-container'), 'visible')
        )

    @staticmethod
    def wait_for_toc(session):
        """
         Waits for the table of contents to become visible.
         """
        WebDriverWait(session, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'a[title="Table of contents"]'))
        )

    def wait_for_persuall(self, session):
        """
        Waits for the main application to become available.
        """
        WebDriverWait(session, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[title="{self.title}"]'))
        )

    def authenticate(self, session):
        """
        Authenticates the session.
        """
        session.get(self.auth_site)
        elem = session.find_element_by_id('eid')
        elem.send_keys(self.user)
        elem = session.find_element_by_id('pw')
        elem.send_keys(self.password)
        elem = session.find_element_by_id('submit')
        elem.click()

    def navigate(self, session):
        """
        Navigates to the document to rip.
        """
        session.get(self.target)
        elem = session.find_element_by_css_selector('.portletBody>p>a')
        elem.click()
        windows = session.window_handles
        session.switch_to_window(windows[-1])
        self.wait_for_persuall(session)
        elem = session.find_element_by_css_selector(f'[title="{self.title}"]')
        elem.click()

    def rip_and_tear(self, session):
        """
        Switches to the frame and returns the processed HTML.
        """
        elem = session.find_element_by_css_selector('.chapter>iframe')
        iframe = elem.get_property('id')
        session.switch_to_frame(iframe)

        return self.embedder.embed_images(session)

    def setup(self, session):
        """
        Runs the setup phase. This includes authenticating and navigating to the document,
        then waiting for it to be ready for ripping.
        """
        self.authenticate(session)
        self.navigate(session)
        self.wait_for_toc(session)
        session.execute_script(
            "document.getElementsByClassName('navbar-fixed-top')[0].style.visibility = 'hidden';"
        )
        session.execute_script(
            "document.getElementById('course-nav').style.visibility = 'hidden';"
        )
        elem = session.find_element_by_css_selector('a[title="Table of contents"]')
        elem.click()
        print('ready')

    def run(self, options, directory='.'):
        """
        Starts the ripping process. Outputs HTML to an output directory.
        """
        session = self.driver(options=options)
        self.setup(session)
        self.pages = len(session.find_elements_by_class_name('outline-item'))

        i = 0
        retries = 0
        bar = ChargingBar('Ripping', max=self.pages)
        bar.index = i
        while i < self.pages and retries <= 10:
            try:
                print(f'.outline-item[data-index="{i}"]')

                WebDriverWait(session, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'.outline-item[data-index="{i}"]'))
                )
                session.execute_script(
                    "Array.prototype.map.call(document.getElementsByClassName('outline-item'), "
                    "ele => {ele.style.display = 'block'});"
                )
                elem = session.find_element_by_css_selector(f'.outline-item[data-index="{i}"]')
                title = elem.text
                elem.click()
                self.wait_for_page(session)
                f = self.rip_and_tear(session)
                with open(f'{directory}/{i:04}_{title}.html', 'w', encoding='utf-8-sig') as outfile:
                    outfile.write(f)
                session.switch_to_default_content()
                i += 1
                retries = 0
                bar.next()
            except:
                retries += 1

        bar.finish()
        session.close()


@click.command()
@click.argument('site')
@click.argument('title')
@click.option('--driver', type=click.Choice(['chrome', 'firefox'], case_sensitive=False), default='chrome')
@click.option('--directory', type=click.Path(dir_okay=True), default='.')
@click.option('--headless/--not-headless', default=True)
@click.option('--username', prompt='OWL Username?')
@click.option('--password', prompt='Password?', hide_input=True)
def rip(driver, username, password, site, title, headless, directory):
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


if __name__ == '__main__':
    rip()
