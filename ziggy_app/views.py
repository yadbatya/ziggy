from idlelib.ReplaceDialog import replace
import string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
import re
from django.contrib.sessions import serializers
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as login_user
# Create your views here.
from ziggy_app.forms import RecipeSearchForm, RegisterForm, LoginForm, NewRecipeForm
from ziggy_app.models import Recipe, Ingredients, Likes, Amounts


@login_required
def home(request):
    # if not request.user.is_authenticated():
    #     return redirect('/login/')
    if request.method == "POST":
        form = RecipeSearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            min_time = data['prep_time_min']
            max_time = data['prep_time_max']
            ingredients_in = data['ingredients']
            ingredients_out = Ingredients.objects.exclude(id__in=ingredients_in)
            diff_levels = data['difficulty_levels']
            name = data.get('name')
            recipes = Recipe.objects.filter(preparation_time__range=(min_time, max_time), difficulty__in=diff_levels,
                                            name__icontains=name).exclude(ingredients__in=ingredients_out)
        else:
            recipes = []
    else:
        recipes = Recipe.objects.all()[0:10]
        form = RecipeSearchForm()
    return render(request, 'index.html', {'recipes': recipes, 'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = authenticate(username=cleaned_data.get('username'), password=cleaned_data.get('password'))
            if user:
                login_user(request, user)
                return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def recipe_page(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    # amounts = Amounts.objects.filter(recipe=recipe)
    liked = Likes.objects.get_or_create(liker=request.user, liked=recipe)[0]
    likes_amount = Likes.objects.filter(liked=recipe, like=True).count()
    return render(request, 'recipe.html', {'recipe': recipe, 'liked': liked, 'likes': likes_amount})#, 'amounts': amounts})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            User.objects.create_user(username=cleaned_data.get('username'), password=cleaned_data.get('password'))
            user = authenticate(username=cleaned_data.get('username'), password=cleaned_data.get('password'))
            if user:
                login_user(request, user)
                return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def add(request):
    if request.method == 'POST':
        form = NewRecipeForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('/add/' + str(instance.id) + "/")
    else:
        form = NewRecipeForm(initial={'user': request.user})
    return render(request, 'add.html', {'form': form})


@login_required
def finish_add(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    if recipe.ingredients.exists():
        return redirect('/')
    if request.method == 'POST':
        extra = int(request.POST['count'])
        for i in xrange(extra):
            ing_name = request.POST.get('ingredient_' + str(i+1))
            if ing_name:
                if re.match('[a-zA-Z ]+', ing_name):
                    ing_name_normalized = string.capwords(ing_name)
                    if ing_name_normalized:
                        ing_amount = request.POST.get('ingredient_' + str(i+1) + "_amount")
                        if ing_amount:
                            ing_unit = request.POST.get('ingredient_' + str(i+1) + "_unit")
                            if ing_unit:
                                ing = Ingredients.objects.get_or_create(name=ing_name_normalized)[0]
                                Amounts.objects.create(recipe=recipe, ingredient=ing, amount=ing_amount, unit=ing_unit)
                        # recipe.ingredients.add(ing[0])
        recipe.instructions = request.POST.get('instructions')
        recipe.save()
        return redirect('/')
    return render(request, 'ingredients.html', {'recipe': recipe})


@login_required
def like(request):
    recipe_id = request.GET['recipe_id']
    user_id = request.GET['user_id']
    user = User.objects.get(id=user_id)
    if request.user != user:
        return HttpResponse('', status=500)
    recipe = Recipe.objects.get(id=recipe_id)
    like_obj = Likes.objects.get(liker=user, liked=recipe)
    like_obj.like = not like_obj.like
    like_obj.save()
    likes_amount = Likes.objects.filter(liked=recipe, like=True).count()
    jsonized = json.dumps({'likes': likes_amount, 'like_str': like_obj.to_button()})
    return HttpResponse(jsonized, content_type='application/json')


@login_required
def user_page(request, user_id):
    cur_user = User.objects.get(id=user_id)
    return render(request, 'user.html', {'cur_user': cur_user})


@login_required
def likes(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    likes_to_recipe = Likes.objects.filter(liked=recipe, like=True)
    return render(request, 'likes.html', {'likes': likes_to_recipe})


# @login_required
# def autocomplete(request):
#     try:
#         word = request.GET.get('word')
#         possibilities = Ingredients.objects.filter(name__istartswith=word)
#         if not possibilities:
#             possibilities = []
#         # ret = []
#         # for x in possibilities:
#         #     ret.append(x.name)
#         serialized_possibilities = serializers.serialize('json', possibilities)
#         # print possibilities
#         jsoned_possibilities = json.dumps({'possibilities': serialized_possibilities}, cls=DjangoJSONEncoder)
#         # x = json.loads(jsoned_possibilities)
#         # print x
#         # jsoned_possibilities = json.dumps({'possibilities': ret})
#         print jsoned_possibilities
#         return HttpResponse(jsoned_possibilities)
#     except:
#         import tracebackef get
#         traceback.print_exc()


@login_required
def get_ingredients(request):
    ingredients = Ingredients.objects.all()
    ingredients = [i.name for i in ingredients]
    # print ingredients
    # ingredients = serializers.serialize('json', ingredients)
    # print ingredients
    ingredients = json.dumps(ingredients)
    return HttpResponse(ingredients, content_type='application/json')