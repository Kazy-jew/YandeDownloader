import settings


class Site:

    def __init__(self, site='yande.re'):
        self.site = site
        self.date_link = settings.config["yande"]["weburl"][0]
        self.post_link = settings.config["yande"]["weburl"][1]
        self.tag_link = settings.config["yande"]["weburl"][2]
        self.site_tag = settings.config["yande"]["tag"]
        self.prefix = settings.config["yande"]["prefix"]
        self.dl_path = settings.config["yande"]["location"]
        self.use_js = settings.config["yande"]["javascript"]
        self.chrome_profile = settings.config["chrome_profile"]
        self.chrome_binary = settings.config['chrome_path']
        self.config = settings.config['yande']

    def set_site(self, site):
        if site in ['yande.re', 'yande', 'y']:
            self.site_tag = settings.config["yande"]["tag"]
            self.site = settings.config["yande"]["site"]
            self.prefix = settings.config["yande"]["prefix"]
            self.date_link = settings.config["yande"]["weburl"][0]
            self.post_link = settings.config["yande"]["weburl"][1]
            self.tag_link = settings.config["yande"]["weburl"][2]
            self.dl_path = settings.config["yande"]["location"]
            self.use_js = settings.config["yande"]["javascript"]
            self.config = settings.config['yande']
        elif site in ['konachan', 'konachan.com', 'k']:
            self.site_tag = settings.config["konachan"]["tag"]
            self.site = settings.config["konachan"]["site"]
            self.prefix = settings.config["konachan"]["prefix"]
            self.date_link = settings.config["konachan"]["weburl"][0]
            self.post_link = settings.config["konachan"]["weburl"][1]
            self.tag_link = settings.config["konachan"]["weburl"][2]
            self.dl_path = settings.config["konachan"]["location"]
            self.use_js = settings.config["konachan"]["javascript"]
            self.config = settings.config['konachan']
        elif site in ['minitokyo', 'm']:
            self.site_tag = settings.config["minitokyo"]["tag"]
            self.site = settings.config["minitokyo"]["site"]
            self.date_link = ''
            self.prefix = settings.config["minitokyo"]["prefix"]
            self.post_link = settings.config["minitokyo"]["weburl"][0]
            self.dl_path = settings.config["minitokyo"]["location"]
            self.use_js = settings.config["minitokyo"]["javascript"]
            self.config = settings.config['minitokyo']
        else:
            raise Exception("No a Valid Site!")
