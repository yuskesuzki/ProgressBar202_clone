import datetime
import os
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

    def calculate_progress(self):
        """1年の進捗率を計算する"""
        start = datetime.datetime(self.year, 1, 1)
        end = datetime.datetime(self.year + 1, 1, 1)
        total_seconds = (end - start).total_seconds()
        elapsed_seconds = (self.now - start).total_seconds()

        percent = (elapsed_seconds / total_seconds) * 100
        return int(percent)

    def generate_image(self, percent):
        """プログレスバー画像を生成する"""
        width, height = 600, 120
        bg_color = (255, 255, 255)
        border_color = (0, 0, 0)

        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # 外枠 (ProgressBar202_風のシンプルな矩形)
        padding_x, padding_y = 40, 40
        bar_height = 40
        draw.rectangle([padding_x, padding_y, width - padding_x, padding_y + bar_height], outline=border_color, width=3)

        # 中身の塗りつぶし
        inner_width = (width - 2 * padding_x - 10) * (percent / 100)
        if inner_width > 0:
            draw.rectangle([padding_x + 5, padding_y + 5, padding_x + 5 + inner_width, padding_y + bar_height - 5], fill=border_color)
        img_filename = f"progress_{percent}.png"
        img_path = os.path.join(self.image_dir, img_filename)
        img.save(img_path)
        return img_filename

    def generate_ogp_html(self, percent, img_filename):
        """Slackが画像を表示できるようにOGPタグ付きHTMLを生成する"""
        img_url = f"{self.base_url}/images/{img_filename}"
        title = f"{self.year} is {percent}% complete."

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="Year Progress Tracker">
    <meta property="og:image" content="{img_url}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{img_url}">
</head>
<body style="text-align:center; font-family:sans-serif; padding-top:50px;">
    <h1>{title}</h1>
    <img src="{img_url}" alt="Progress Bar" style="max-width:100%; border:1px solid #ccc;">
</body>
</html>"""

        html_filename = f"p{percent}.html"
        html_path = os.path.join(self.image_dir, html_filename)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return html_filename

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

        # リンク先を画像ではなく「OGP付きHTML」にする
        html_url = f"{self.base_url}/images/{html_filename}"
        fe.link(href=html_url)

        # RSSリーダー用のHTMLコンテンツ
        img_url = f"{self.base_url}/images/{img_filename}"
        fe.content(f"{content_text}<br><img src='{img_url}'>", type='html')
        fe.published(datetime.datetime.now(datetime.timezone.utc))

        fg.rss_file(self.rss_file, pretty=True)

    def run(self):
        current_p = self.calculate_progress()

        date_str = self.now.strftime("%Y-%m-%d")
        print(f"today: {date_str}")

        # 前回の値をチェック
        last_p = -1
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                last_p = int(f.read().strip())

        if current_p > last_p:
            print(f"Updating: {current_p}%")
            img_file = self.generate_image(current_p)
            html_file = self.generate_ogp_html(current_p, img_file)
            self.update_rss(current_p, img_file, html_file)
            with open(self.state_file, "w") as f:
                f.write(str(current_p))
            return True
        else:
            print(f"Not updating: now {current_p}%")
            return False

if __name__ == "__main__":
    cloner = YearProgressCloner()
    cloner.run()
