__author__ = 'amir'
from django import forms
from django.contrib.auth.models import User
from ziggy_app.models import Recipe, DIFFICULTY_LEVEL, Ingredients, Amounts


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError("this username already exsits")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class NewRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ("user", "upload_date", "ingredients", "instructions")


class NewAmountForm(forms.ModelForm):
    class Meta:
        model = Amounts
        exclude = ("recipe", "ingredient")


# class IngredientForm(forms.Form):
#     ingredient_0 = forms.CharField()
#     extra_field_count = forms.CharField(widget=forms.HiddenInput())
#
#     def __init__(self, *args, **kwargs):
#         extra_fields = kwargs.pop('extra', 0)
#         if int(extra_fields):
#             data = args[0]
#         super(IngredientForm, self).__init__(*args, **kwargs)
#         self.fields['extra_field_count'].initial = extra_fields
#         print "extra_fields -", extra_fields
#         if int(extra_fields): print data
#         for i in xrange(int(extra_fields)):
#             # generate extra fields in the number specified via extra_fields
#             self.fields['ingredient_{index}'.format(index=i+1)] = forms.CharField()
#             self.fields['ingredient_{index}'.format(index=i+1)].initial = data.get('extra_field_' + str(i+1))
#         print self.fields['ingredient_0'].__dict__
#         if int(extra_fields): print self.fields['ingredient_1'].__dict__
#         # print self.ingredient_0
#         # if extra_fields: print self.ingredient_1


class RecipeSearchForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    prep_time_min = forms.IntegerField(required=False)
    prep_time_max = forms.IntegerField(required=False)
    ingredients = forms.ModelMultipleChoiceField(Ingredients.objects.all(), widget=forms.CheckboxSelectMultiple,
                                                 required=False)
    difficulty_levels = forms.MultipleChoiceField(choices=DIFFICULTY_LEVEL, widget=forms.CheckboxSelectMultiple,
                                                  required=False)

    def clean(self):
        cleaned_data = super(RecipeSearchForm, self).clean()
        if not cleaned_data.get('prep_time_min'):
            cleaned_data['prep_time_min'] = 0
        if not cleaned_data.get('prep_time_max'):
            cleaned_data['prep_time_max'] = 10000
        if cleaned_data['prep_time_min'] > cleaned_data['prep_time_max']:
            raise forms.ValidationError("min cant be bigger than max")
        if not cleaned_data.get('difficulty_levels'):
            cleaned_data['difficulty_levels'] = [1, 2, 3, 4, 5]
        if not cleaned_data.get('ingredients'):
            cleaned_data['ingredients'] = Ingredients.objects.all()
        return cleaned_data