from src.interface import Yande, Konachan, Minitokyo


def run_main():
    console_log = input("""Please Select Downloader(default: yande.re, enter q to quit)
    1.yande.re    2.konachan   3.minitokyo \nEnter you choice: """)
    if console_log in ['2', 'k', 'konachan', 'konachan.com']:
        site_crawler = Konachan()
    elif console_log in ['3', 'm', 'minitokyo']:
        site_crawler = Minitokyo()
    elif console_log == 'q':
        raise SystemExit(-1, 'Manual Quit')
    else:
        site_crawler = Yande()
    site_crawler.run()


if __name__ == '__main__':
    run_main()
