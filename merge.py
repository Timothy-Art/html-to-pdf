import click
import os
from progress.bar import ChargingBar
from PyPDF2.merger import PdfFileMerger
import weasyprint


class PageMerger:
    @staticmethod
    def run(directory, output):
        """
        Compiles a directory of HTML into a single pdf.

        :param directory: Directory to search.
        :param output: filename to write to.
        """
        files = [f for f in os.listdir(directory) if f[-5:] == '.html']
        files.sort(key=lambda x: int(x[:-5]))
        with ChargingBar('Converting', max=len(files)) as progress:
            for file in files:
                html = weasyprint.HTML(filename=f'{directory}/{file}')
                html.write_pdf(target=f"{directory}/{file[:-5]}.pdf")
                progress.next()

        merger = PdfFileMerger()
        with ChargingBar('Merging', max=len(files) + 1) as progress:
            for file in files:
                reader = open(f"{directory}/{file[:-5]}.pdf")
                merger.append(reader, bookmark=f"{file[:-5]}", import_bookmarks=False)
                progress.next()
            merger.write(output)
            progress.next()
        for file in files:
            os.remove(f"{directory}/{file[:-5]}.html")
            os.remove(f"{directory}/{file[:-5]}.pdf")


@click.command()
@click.option('--directory', type=click.Path(dir_okay=True), default='.')
@click.option('--output', default='output.pdf')
def merge(directory, output):
    if os.path.isdir(directory):
        os.mkdir(directory)
    PageMerger.run(directory=directory, output=output)


if __name__ == '__main__':
    merge()
