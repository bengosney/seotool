class RemoveCMSBar:
    def __init__(self, crawler):
        self.crawler = crawler

    def process_html(self, html):
        try:
            html.find('div', id="cms_front_end_bar").decompose()
        except AttributeError:
            pass

        return html
