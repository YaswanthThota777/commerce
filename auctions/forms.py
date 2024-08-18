from django import forms
from .models import AuctionListing, Category
from .models import Bid, Comment

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class AuctionListingForm(forms.ModelForm):
    new_category = forms.CharField(max_length=64, required=False, help_text="Add a new category if it doesn't exist.")

    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'current_price', 'image_url', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'starting_bid': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def save(self, commit=True):
        listing = super().save(commit=False)
        new_category_name = self.cleaned_data.get('new_category')

        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
            listing.category = category

        if commit:
            listing.save()

        return listing
