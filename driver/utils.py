from selenium import webdriver


class DriverFactory:
    """
    Factory for dynamically setting which driver and driver options to use.
    """
    @staticmethod
    def get_webdriver(driver):
        if driver == 'chrome':
            return webdriver.Chrome
        elif driver == 'firefox':
            return webdriver.Firefox
        else:
            raise ValueError(f"driver {driver} not supported!")

    @staticmethod
    def get_driveropts(driver):
        if driver == 'chrome':
            return webdriver.ChromeOptions
        elif driver == 'firefox':
            return webdriver.FirefoxOptions
        else:
            raise ValueError(f"driver {driver} not supported!")


def get_driver(driver, headless):
    driver = DriverFactory.get_webdriver(driver)()
    options = DriverFactory.get_driveropts(driver)()
    if headless:
        options.add_argument('headless')
    options.add_argument('--no-sandbox')

    return driver, options
