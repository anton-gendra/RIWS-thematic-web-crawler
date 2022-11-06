from django import forms

class FilterForm(forms.Form):

    CATEGORY_CHOICES = (
        ('none', '-'),
        ('ME', '1'),
        ('YOU', '2'),
        ('WE', '3'),
        )

    BRAND_CHOICES = (
        ('none', '-'),
        ('tetas', 'tetas'),
        ('tetitas', 'tetitas'),
        ('bufas', 'bufas'),
        ('bufarracas', 'bufarracas'),
    )

    name = forms.CharField(label="Name", required = False)
    minPrice = forms.CharField(label="Min. Price", required = False)
    maxPrice = forms.CharField(label="Max. Price", required = False)
    category_select = forms.ChoiceField(label="Category", choices=CATEGORY_CHOICES, required = False)
    brand_select = forms.ChoiceField(label="Brand", choices=BRAND_CHOICES, required = False)
