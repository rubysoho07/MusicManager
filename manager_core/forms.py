# -*- coding: utf-8 -*-
from django import forms

SEARCH_TYPE_CHOICES = (
    ("artist", u"아티스트"),
    ("album", u"앨범명"),
)


class AlbumSearchForm(forms.Form):
    search_type = forms.ChoiceField(label="", choices=SEARCH_TYPE_CHOICES)
    keyword = forms.CharField(label="")
