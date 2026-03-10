import datetime
import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from feedgen.feed import FeedGenerator

class YearProgressCloner:
    def __init__(self, year=None):
        self.now = datetime.datetime.now()
        self.year = year or self.now.year
        self.image_dir = "images"
        self.state_file = "last_percent.txt"
        self.rss_file = "rss.xml"

        self.github_user = "yuskesuzki"
        self.repo_name = "ProgressBar202_clone"
        self.base_url = f"https://{self.github_user}.github.io/{self.repo_name}"

        os.makedirs(self.image_dir, exist_ok=True)

    # (calculate_progress, generate_image, generate_ogp_html は前回と同様)
    def calculate_progress(self):
        start = datetime.datetime(self.year, 1, 1)
        end = datetime.datetime(self.year + 1, 1, 1)
        total_seconds = (end - start).total_seconds()
        elapsed_seconds = (self.now - start).total_seconds()
        return int((elapsed_seconds / total_seconds) * 100)

    def generate_image(self, percent):
        width, height = 600, 120
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, 560, 80], outline=(0, 0, 0), width=3)
        inner_w = (520 - 10) * (percent / 100)
        if inner_w > 0:
            draw.rectangle([45, 45, 45 + inner_w, 75], fill=(0, 0, 0))
        filename = f"progress_{percent}.png"
        img.save(os.path.join(self.image_dir, filename))
        return filename

    def generate_ogp_html(self, percent, img_file):
        img_url = f"{self.base_url}/images/{img_file}"
        title = f"{self.year} is {percent}% complete."
        html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><meta property="og:image" content="{img_url}"><meta property="og:title" content="{title}"></head><body><img src="{img_url}"></body></html>'
        filename = f"p{percent}.html"
        with open(os.path.join(self.image_dir, filename), "w", encoding="utf-8") as f:
            f.write(html)
        return filename

    def update_rss(self, percent, img_filename, html_filename):
        fg = FeedGenerator()
        fg.id(f"year-progress-{self.year}")
        fg.title(f"Year Progress {self.year}")
        fg.link(href=self.base_url, rel='alternate')
        fg.description(f"Clone of Year Progress for {self.year}")

        fe = fg.add_entry()
        content_text = f"{self.year} is {percent}% complete."
        fe.id(f"{self.year}-{percent}")
        fe.title(content_text)
        fe.link(href=f"{self.base_url}/images/{html_filename}")
        fe.description(content_text)
        fe.published(datetime.datetime.now(datetime.timezone.utc))

        # XMLを一度生成してElementTreeで読み込む
        rss_bytes = fg.rss_str(pretty=True)
        ET.register_namespace('content', "http://purl.org/rss/1.0/modules/content/")
        root = ET.fromstring(rss_bytes)

        # content:encodedタグを手動で追加
        img_url = f"{self.base_url}/images/{img_filename}?v={percent}"
        item = root.find('.//item')
        if item is not None:
            # {Namespace}Tag の形式で追加
            content_encoded = ET.SubElement(item, '{http://purl.org/rss/1.0/modules/content/}encoded')
            content_encoded.text = f'{content_text}<br><img src="{img_url}" />'

        # ファイルに書き出し
        tree = ET.ElementTree(root)
        with open(self.rss_file, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)

    def run(self):
        curr = self.calculate_progress()
        last = -1
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                last = int(f.read().strip())

        # テスト時はここを > ではなく != にするか、last_percent.txtを書き換えてください
        if curr > last:
            print(f"Updating: now {curr}%")
            img = self.generate_image(curr)
            html = self.generate_ogp_html(curr, img)
            self.update_rss(curr, img, html)
            with open(self.state_file, "w") as f:
                f.write(str(curr))
            print(f"✅ RSS updated: {curr}%")
            return True
        else:
            print(f"Not updating: now {curr}%")
            return False

if __name__ == "__main__":
    cloner = YearProgressCloner()
    cloner.run()
