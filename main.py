import datetime
import os
from PIL import Image, ImageDraw
from feedgen.feed import FeedGenerator

class YearProgressCloner:
    base_url = "https://github.com/yuskesuzki/ProgressBar202_clone"

    def __init__(self, year=None):
        self.now = datetime.datetime.now()
        self.year = year or self.now.year
        self.image_dir = "images"
        self.state_file = "last_percent.txt"
        self.rss_file = "rss.xml"
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

        img_path = os.path.join(self.image_dir, f"progress_{percent}.png")
        img.save(img_path)
        return img_path

    def update_rss(self, percent, img_path):
        """RSSフィードを生成・更新する"""
        fg = FeedGenerator()
        fg.id(f"year-progress-{self.year}")
        fg.title(f"Year Progress {self.year}")
        fg.link(href=self.base_url, rel='alternate')
        fg.description(f"Clone of Year Progress for {self.year}")

        fe = fg.add_entry()
        content = f"{self.year} is {percent}% complete."
        fe.id(f"{self.year}-{percent}")
        fe.title(content)

        img_url = f"{self.base_url}/{img_path}"
        fe.content(f"{content}<br><img src='{img_url}'>", type='html')
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
            path = self.generate_image(current_p)
            self.update_rss(current_p, path)
            with open(self.state_file, "w") as f:
                f.write(str(current_p))
            return True
        else:
            print(f"Not updating: now {current_p}%")
            return False

if __name__ == "__main__":
    cloner = YearProgressCloner()
    cloner.run()
