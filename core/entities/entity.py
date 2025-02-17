from __future__ import unicode_literals

from datetime import datetime

from mongoengine import StringField, ListField, DateTimeField
from flask_mongoengine.wtf import model_form

from core.database import Node, TagListField, EntityListField
from core.observables import Tag


class Entity(Node):
    SEARCH_ALIASES = {
        "name": "aliases",
    }

    VERB_DICT = {
        "Malware": {"Actor": "Used by", "TTP": "Leverages"},
        "Actor": {"Malware": "Uses", "TTP": "Leverages"},
        "Company": {},
        "TTP": {"Actor": "Leveraged by", "Malware": "Observed in"},
    }

    DISPLAY_FIELDS = [("name", "Name"), ("tags", "Tags"), ("created", "Created")]

    name = StringField(
        verbose_name="Name",
        required=True,
        unique_with="_cls",
        sparse=True,
        max_length=1024,
    )
    description = StringField(verbose_name="Description")
    tags = ListField(StringField(), verbose_name="Relevant tags")
    created = DateTimeField(default=datetime.utcnow)

    meta = {
        "allow_inheritance": True,
        "indexes": ["tags"],
        "ordering": ["name"],
    }

    def clean(self):
        tags = []
        for t in self.tags:
            if t:
                tags.append(Tag.get_or_create(name=t.lower().strip()))
        self.tags = [t.name for t in tags]

    def __unicode__(self):
        return self.name

    def action(self, target, source, verb=None):
        if not verb:
            if self.__class__.name == target.__class__.__name__:
                verb = "Related {}".format(self.__class__.__name__)
            else:
                verb = Entity.VERB_DICT.get(self.__class__.__name__, {}).get(
                    target.__class__.__name__, "Relates to"
                )
        self.active_link_to(target, verb, source)

    def generate_tags(self):
        return []

    def info(self):
        """Object info.

        When there is no Flask context, url and human_url are not returned and the
        object id is returned instead.
        """
        i = {
            "name": self.name,
            "created": self.created,
            "description": self.description,
            "tags": self.tags,
            "id": str(self.id),
        }
        return i
