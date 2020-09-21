# HTML to PDF

*Code for scraping and compiling online content into a pdf using selenium.*

## Installation

Requires `python>=3.6`

Script requires installation of a Selenium driver of your choice (Chrome/Firefox supported) as well 
as an installation of [weasyprint](https://weasyprint.readthedocs.io/en/latest/install.html) which 
requires supplementary libraries.

## Usage

After installation, command can be run with

```sh
$ python3 rip_and_merge.py SITE TITLE
```

`SITE` - URL of the site where the book portal is.

`TITLE` - Name of the book you want to download.

### Optional Parameters

`--driver` - `(chrome|firefox)` Selenium web driver to use. Defaults to Chrome.

`--directory` - Temporary output directory. Defaults to the current directory.

`--headless/--not-headless` - Whether to run the browser in headless or not. Defaults to headless.

`--output` - Filename to output the pdf to. 
