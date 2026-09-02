"""
JARVIS Universal Launcher
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import shutil

from tools.intent_parser import IntentParser
from tools.multi_command_parser import MultiCommandParser

from tools.command_parser import CommandParser
from tools.windows_app_scanner import WindowsAppScanner
from tools.app_registry import APP_REGISTRY
from tools.browser import BrowserTool


class UniversalLauncher:

    WEBSITE_REGISTRY = {

        "instagram": "https://instagram.com",
        "facebook": "https://facebook.com",
        "youtube": "https://youtube.com",
        "telegram": "https://web.telegram.org",
        "whatsapp": "https://web.whatsapp.com",
        "chatgpt": "https://chat.openai.com",
        "openai": "https://chat.openai.com",
        "github": "https://github.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "linkedin": "https://linkedin.com",
        "twitter": "https://x.com",
        "x": "https://x.com",
        "amazon": "https://amazon.in",
        "flipkart": "https://flipkart.com",
        "netflix": "https://netflix.com",
        "hotstar": "https://hotstar.com",
        "razorpay": "https://razorpay.com",
        "youtube studio": "https://studio.youtube.com",
        "wikipedia": "https://www.wikipedia.org",
        "reddit": "https://www.reddit.com",
        "pinterest": "https://www.pinterest.com",
        "quora": "https://www.quora.com",
        "tumblr": "https://www.tumblr.com",
        "flickr": "https://www.flickr.com",
        "snapchat": "https://www.snapchat.com",
        "tiktok": "https://www.tiktok.com",
        "vimeo": "https://www.vimeo.com",
        "dropbox": "https://www.dropbox.com",
        "onedrive": "https://www.onedrive.com",
        "google drive": "https://drive.google.com",
        "icloud": "https://www.icloud.com",
        "ebay": "https://www.ebay.com",
        "alibaba": "https://www.alibaba.com",
        "hulu": "https://www.hulu.com",
        "disney plus": "https://www.disneyplus.com",
        "hbo max": "https://www.hbomax.com",
        "spotify": "https://www.spotify.com",
        "soundcloud": "https://www.soundcloud.com",
        "apple music": "https://www.apple.com/apple-music",
        "pandora": "https://www.pandora.com",
        "deezer": "https://www.deezer.com",
        "bandcamp": "https://www.bandcamp.com",
        "bbc": "https://www.bbc.com",
        "cnn": "https://www.cnn.com",
        "nytimes": "https://www.nytimes.com",
        "the guardian": "https://www.theguardian.com",
        "forbes": "https://www.forbes.com",
        "bloomberg": "https://www.bloomberg.com",
        "reuters": "https://www.reuters.com",
        "espn": "https://www.espn.com",
        "fox news": "https://www.foxnews.com",
        "nbc news": "https://www.nbcnews.com",
        "cbs news": "https://www.cbsnews.com",
        "abc news": "https://www.abcnews.go.com",
        "msnbc": "https://www.msnbc.com",
        "npr": "https://www.npr.org",
        "wsj": "https://www.wsj.com",
        "yahoo news": "https://news.yahoo.com",
        "buzzfeed": "https://www.buzzfeed.com",
        "huffpost": "https://www.huffpost.com",
        "canva": "https://www.canva.com",
        "slack": "https://www.slack.com",
        "trello": "https://www.trello.com",
        "asana": "https://www.asana.com",
        "zoom": "https://www.zoom.us",
        "skype": "https://www.skype.com",
        "microsoft teams": "https://www.microsoft.com/microsoft-teams",
        "google meet": "https://meet.google.com",
        "webex": "https://www.webex.com",
        "jira": "https://www.atlassian.com/software/jira",
        "notion": "https://www.notion.so",
        "airtable": "https://www.airtable.com",
        "monday": "https://www.monday.com",
        "clickup": "https://www.clickup.com",
        "dropbox paper": "https://www.dropbox.com/paper",
        "confluence": "https://www.atlassian.com/software/confluence",
        "figma": "https://www.figma.com",
        "adobe xd": "https://www.adobe.com/products/xd.html",
        "invision": "https://www.invisionapp.com",
        "microsoft word": "https://www.microsoft.com/microsoft-365/word",
        "google docs": "https://docs.google.com",
        "medium": "https://www.medium.com",
        "wordpress": "https://www.wordpress.com",
        "wix": "https://www.wix.com",
        "squarespace": "https://www.squarespace.com",
        "shopify": "https://www.shopify.com",
        "bigcommerce": "https://www.bigcommerce.com",
        "weebly": "https://www.weebly.com",
        "godaddy": "https://www.godaddy.com",
        "namecheap": "https://www.namecheap.com",
        "bluehost": "https://www.bluehost.com",
        "siteground": "https://www.siteground.com",
        "hostgator": "https://www.hostgator.com",
        "dreamhost": "https://www.dreamhost.com",
        "a2 hosting": "https://www.a2hosting.com",
        "inmotion hosting": "https://www.inmotionhosting.com",
        "digitalocean": "https://www.digitalocean.com",
        "linode": "https://www.linode.com",
        "aws": "https://aws.amazon.com",
        "azure": "https://azure.microsoft.com",
        "google cloud": "https://cloud.google.com",
        "heroku": "https://www.heroku.com",
        "gitlab": "https://www.gitlab.com",
        "bitbucket": "https://bitbucket.org",
        "codepen": "https://codepen.io",
        "jsfiddle": "https://jsfiddle.net",
        "repl.it": "https://repl.it",
        "stack overflow": "https://stackoverflow.com",
        "stackoverflow careers": "https://stackoverflow.com/jobs",
        "glassdoor": "https://www.glassdoor.com",
        "indeed": "https://www.indeed.com",
        "linkedin jobs": "https://www.linkedin.com/jobs",
        "monster": "https://www.monster.com",
        "simplyhired": "https://www.simplyhired.com",
        "angel.co": "https://angel.co",
        "github jobs": "https://jobs.github.com",
        "ziprecruiter": "https://www.ziprecruiter.com",
        "careerbuilder": "https://www.careerbuilder.com",
        "snagajob": "https://www.snagajob.com",
        "dice": "https://www.dice.com",
        "jobs": "https://www.jobs.com",
        "bamboohr": "https://www.bamboohr.com",
        "workday": "https://www.workday.com",
        "adp": "https://www.adp.com",
        "sap successfactors": "https://www.sap.com/products/hcm.html",
        "oracle hcm": "https://www.oracle.com/applications/human-capital-management",
        "zenefits": "https://www.zenefits.com",
        "paycor": "https://www.paycor.com",
        "paycom": "https://www.paycom.com",
        "gusto": "https://www.gusto.com",
        "square": "https://squareup.com",
        "stripe": "https://www.stripe.com",
        "paypal": "https://www.paypal.com",
        "venmo": "https://www.venmo.com",
        "cash app": "https://cash.app",
        "robinhood": "https://www.robinhood.com",
        "etrade": "https://www.etrade.com",
        "fidelity": "https://www.fidelity.com",
        "charles schwab": "https://www.schwab.com",
        "vanguard": "https://investor.vanguard.com",
        "td ameritrade": "https://www.tdameritrade.com",
        "coinbase": "https://www.coinbase.com",
        "binance": "https://www.binance.com",
        "kraken": "https://www.kraken.com",
        "blockchain": "https://www.blockchain.com",
        "gemini": "https://www.gemini.com",
        "bitfinex": "https://www.bitfinex.com",
        "bitstamp": "https://www.bitstamp.net",
        "bittrex": "https://www.bittrex.com",
        "okex": "https://www.okex.com",
        "poloniex": "https://www.poloniex.com",
        "coindesk": "https://www.coindesk.com",
        "cointelegraph": "https://www.cointelegraph.com",
        "decrypt": "https://www.decrypt.co",
        "cryptoslate": "https://www.cryptoslate.com",
        "cryptonews": "https://www.cryptonews.com",
        "coinmarketcap": "https://www.coinmarketcap.com",
        "coingecko": "https://www.coingecko.com",
        "messari": "https://www.messari.io",
        "icodrops": "https://www.icodrops.com",
        "tokenmarket": "https://www.tokenmarket.net",
        "coinpaprika": "https://www.coinpaprika.com",
        "cryptocompare": "https://www.cryptocompare.com",
        "coincheckup": "https://www.coincheckup.com",
        "cryptobriefing": "https://www.cryptobriefing.com",
        "blockonomi": "https://www.blockonomi.com",
        "coininsider": "https://www.coininsider.com",
        "newsbtc": "https://www.newsbtc.com",
        "bitcoin.com": "https://www.bitcoin.com",
        "ethereum.org": "https://www.ethereum.org",
        "litecoin.com": "https://www.litecoin.com",
        "ripple.com": "https://www.ripple.com",
        "cardano.org": "https://www.cardano.org",
        "stellarlumens.com": "https://www.stellarlumens.com",
        "tezos.com": "https://www.tezos.com",
        "eos.io": "https://www.eos.io",
        "neo.org": "https://www.neo.org",
        "iota.org": "https://www.iota.org",
        "monero.org": "https://www.monero.org",
        "zcash.org": "https://www.zcash.org",
        "dash.org": "https://www.dash.org",
        "dogecoin.com": "https://www.dogecoin.com",
        "gpt": "https://www.chatgpt.com/",
    }

    def __init__(self):

        self.scanner = WindowsAppScanner()
        # Multi command parser
        self.multi_parser = MultiCommandParser()

        # Single command parser
        self.command_parser = CommandParser()

        # Intent parser
        self.intent = IntentParser()

        alias_file = os.path.join(
            "config",
            "app_aliases.json"
        )

        if os.path.exists(alias_file):

            with open(
                alias_file,
                "r",
                encoding="utf-8"
            ) as f:

                self.aliases = json.load(f)

        else:

            self.aliases = {}

    def launch_multiple(self, command: str):

        commands = self.multi_parser.split(command)

        results = []

        for item in commands:

            result = self.launch(item)

            results.append(result)

        return results

    def launch(self, target: str):

        target = self.command_parser.parse(target)

        intent = self.intent.parse(target)

        target = intent["target"]

        query = intent["query"]

        target = self.aliases.get(
            target,
            target
        )

        # -----------------------------
        # Installed Windows Applications
        # -----------------------------

        exe = self.scanner.get(target)

        if exe:

            subprocess.Popen(exe)

            return {

                "status": "success",
                "type": "installed_app",
                "path": exe

            }

        # -----------------------------------
        # PATH Executables
        # -----------------------------------

        exe = shutil.which(target)

        if exe:
            subprocess.Popen(exe)

            return {

                "status": "success",
                "type": "path_app",
                "path": exe
            }    

        # -----------------------------
        # Manual Registry Apps
        # -----------------------------

        if target in APP_REGISTRY:

            executable = APP_REGISTRY[target]

            try:

                subprocess.Popen(executable)

                return {

                    "status": "success",
                    "type": "application",
                    "name": target

                }

            except Exception:

                pass

        # -----------------------------
        # Websites
        # -----------------------------

        if target in self.WEBSITE_REGISTRY:

            url = self.WEBSITE_REGISTRY[target]
            if query:
                if target == "google":
                    url = (
                        "https://www.google.com/search?q="
                        + urllib.parse.quote(query)
                    )

                elif target == "youtube":
                    url = (
                        "https://www.youtube.com/results?search_query="
                        + urllib.parse.quote(query)
                    )    

                elif target == "github":
                    url = (
                        "https://github.com/search?q="
                        + urllib.parse.quote(query)
                    )

            BrowserTool.open(url)

            return {

                "status": "success",

                "type": "website",

                "name": target,

                "query": query

            }

        # -----------------------------
        # Google Search
        # -----------------------------

        query = urllib.parse.quote(target)

        BrowserTool.open(
            f"https://www.google.com/search?q={query}"
        )

        return {

            "status": "success",
            "type": "search",
            "query": target

        }