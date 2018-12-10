# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import json
from datetime import datetime
import os.path

class asky(kp.Plugin):
    """
    Search for asky from asky.io and copy then to your clipboard
    This plugin was based on: https://github.com/Fuhrmann/keypirinha-gitmoji
    """

    ASKY_URL = "https://api.asky.io/art"
    DAYS_KEEP_CACHE = 7
    ITEMCAT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self.askys = []

    def on_start(self):
        self.generate_cache()
        self.get_asky()
        pass

    def on_catalog(self):
        self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label="asky",
                short_desc="Search ascii art from asky.io and copy them to your clipboard",
                target="asky",
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            )
        ])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[0].category() != kp.ItemCategory.KEYWORD:
            return

        suggestions = self.filter_asky(user_input)
        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.LABEL_ASC)

    def filter_asky(self, user_input):
        return list(filter(lambda item: self.has_title_description(item, user_input), self.askys))

    def has_title_description(self, item, user_input):
        if user_input.lower() in item.label().lower() or user_input.lower() in item.short_desc().lower():
            return item

        return False

    def on_execute(self, item, action):
        kpu.set_clipboard(item.target())

    def generate_cache(self):
        cache_path = self.get_cache_path()
        should_generate = False
        try:
            last_modified = datetime.fromtimestamp(os.path.getmtime(cache_path)).date()
            if ((last_modified - datetime.today().date()).days > self.DAYS_KEEP_CACHE):
                should_generate = True
        except Exception as exc:
            should_generate = True

        if not should_generate:
            return False

        try:
            opener = kpnet.build_urllib_opener()
            with opener.open(self.ASKY_URL) as request:
                response = request.read()
        except Exception as exc:
            self.err("Could not reach the asky repository file to generate the cache: ", exc)

        data = json.loads(response)
        with open(cache_path, "w") as index_file:
            json.dump(data, index_file, indent=2)

    def get_asky(self):
        if not self.askys:
            with open(self.get_cache_path(), "r") as asky_file:
                data = json.loads(asky_file.read())
            for item in data:
                suggestion = self.create_item(
                    category=self.ITEMCAT,
                    label=item['content'],
                    short_desc=item['title'],
                    target=item['content'],
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE
                )

                self.asky.append(suggestion)

        return self.asky

    def get_cache_path(self):
        cache_path = self.get_package_cache_path(True)
        return os.path.join(cache_path, 'asky.json')