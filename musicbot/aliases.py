import logging
import shutil
import json
from pathlib import Path

from .exceptions import HelpfulError

log = logging.getLogger(__name__)


class Aliases:
    def __init__(self, aliases_file):
        self.aliases_file = Path(aliases_file)
        self.aliases_seed = AliasesDefault.aliases_seed
        self.aliases = AliasesDefault.aliases

        # find aliases file
        if not self.aliases_file.is_file():
            example_aliases = Path("config/example_aliases.json")
            if example_aliases.is_file():
                shutil.copy(str(example_aliases), str(self.aliases_file))
                log.warning("Aliases file not found, copying example_aliases.json")
            else:
                raise HelpfulError(
                    "Your aliases files are missing. Neither aliases.json nor example_aliases.json were found.",
                    "Grab the files back from the archive or remake them yourself and copy paste the content "
                    "from the repo. Stop removing important files!",
                )

        # parse json
        with self.aliases_file.open() as f:
            try:
                self.aliases_seed = json.load(f)
            except:
                raise HelpfulError(
                    "Failed to parse aliases file.",
                    "Ensure your {} is a valid json file and restart the bot.".format(
                        str(self.aliases_file)
                    ),
                )

        # construct
        for cmd, aliases in self.aliases_seed.items():
            if not isinstance(cmd, str) or not isinstance(aliases, list):
                raise HelpfulError(
                    "Failed to parse aliases file.",
                    "See documents and config {} properly!".format(
                        str(self.aliases_file)
                    ),
                )
            self.aliases.update({alias: cmd for alias in aliases})

    def get(self, arg):
        """
        Return cmd name (string) that given arg points.
        If arg is not registered as alias, empty string will be returned.
        supposed to be called from bot.on_message
        """
        ret = self.aliases.get(arg)
        return ret if ret else ""

    def create_alias(self, alias_name, alias_for):
        """
        Creates new alias that will be added to current alias json in given config
        """
        ret = self.aliases.get(alias_name)
        if ret != "":
            raise HelpfulError(
                "Alias already exists:",
                "{alias_name} is an alias for {ret}".format(
                    alias_name=alias_name, ret=ret
                ),
            )

        self.aliases[alias_name] = "[p {alias_for}]".format(alias_for=alias_for)
        
        with open(self.aliases_file, "w") as outfile:
            json.dump(self.aliases, outfile)
            outfile.flush()
            outfile.close()


class AliasesDefault:
    aliases_file = "config/aliases.json"
    aliases_seed = {}
    aliases = {}
