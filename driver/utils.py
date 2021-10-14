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


def get_driver(driver_name, headless):
    driver = DriverFactory.get_webdriver(driver_name)()
    options = DriverFactory.get_driveropts(driver_name)()
    if headless:
        options.add_argument('--headless')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    return driver, options
