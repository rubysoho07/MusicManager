from django import forms

SEARCH_TYPE_CHOICES = (
    ("artist", u"아티스트"),
    ("album", u"앨범명"),
)


class AlbumSearchForm(forms.Form):
    """Form for searching albums from database."""

    search_type = forms.ChoiceField(label="", choices=SEARCH_TYPE_CHOICES)
    keyword = forms.CharField(label="")


class AlbumParseRequestForm(forms.Form):
    """Form for requesting to parse album from music information sites."""

    album_url = forms.CharField(label="")
