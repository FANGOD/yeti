import logging
from datetime import timedelta

from core import Feed
from core.errors import ObservableValidationError
from core.observables import Ip
from core.config.config import yeti_config


class AbuseIPDB(Feed):
    default_values = {
        "frequency": timedelta(hours=5),
        "name": "AbuseIPDB",
        "source": "https://api.abuseipdb.com/api/v2/blacklist",
        "description": "Black List IP generated by AbuseIPDB",
    }

    def update(self):
        api_key = yeti_config.get("abuseIPDB", "key")

        if api_key:
            self.source = (
                "https://api.abuseipdb.com/api/v2/blacklist?&key=%s&plaintext&limit=10000"
                % (api_key)
            )
            # change the limit rate if you subscribe to a paid plan
            for line in self.update_lines():
                self.analyze(line)
        else:
            logging.error("Your abuseIPDB API key is not set in the yeti.conf file")

    def analyze(self, line):
        line = line.strip()

        ip = line

        context = {"source": self.name}

        try:
            ip = Ip.get_or_create(value=ip)
            ip.add_context(context)
            ip.add_source(self.name)
            ip.tag("abuseIPDB")
        except ObservableValidationError as e:
            raise logging.error(e)