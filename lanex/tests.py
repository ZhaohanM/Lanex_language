from django.test import TestCase
import lanex.models
import os, re, inspect, tempfile
from django.contrib.auth.models import User
from lanex import forms
from django.urls import reverse, resolve
from django.conf import settings
from django.db import models
from django.forms import fields as django_fields
from django.forms import models as django_field_models
from location_field.forms.plain import PlainLocationField


'''
Helper method which adds the language to the language model, returning a reference to the model 
  instance created or retrieved as a result, having name,slug and picture as parameteres.
'''
def add_language(name, slug, picture):
    language = lanex.models.Language.objects.get_or_create(name=name,
                                                            slug=slug,
                                                            picture=picture)[0]
    language.slug = slug
    language.picture = picture
    language.save()
    return language


'''
Helper method to create user object.
'''
def create_user_object():
    user = User.objects.get_or_create(username='ausername', first_name='afname', last_name='alname', email='test@email.com')[0]
    user.set_password('apassword4testing')
    user.save()
    return user


class IndexViewTesting(TestCase):
    '''
    Displays the appropriate message if no languages exist.
    '''
    def test_index_view_with_no_languages(self):
        response = self.client.get(reverse('lanex:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no requests present.')
        self.assertQuerysetEqual(response.context['requests'], [])


    def test_location_lanex(self):
        """
        Tests to see that view location matches  expected url written into url search bar by users  (hardcoded)'
        """
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)


    """
    Tests to see that the anticipated relative view is able to call upon the index view. 
    """
    def test_url_accessibility(self):
        response = self.client.get(reverse('lanex:index'))
        self.assertEquals(response.status_code, 200)


    """
    Tests to check that the index view uses its respective template.
    """
    def test_template_matches(self):
        response = self.client.get(reverse('lanex:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lanex/index.html')


class ExploreViewTesting(TestCase):
    '''
    Displays the appropriate message if no languages exist.
    '''
    def test_explore_view_with_no_languages(self):
        response = self.client.get(reverse('lanex:explore'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no requests present.')
        self.assertQuerysetEqual(response.context['requests'], [])


    '''
    Checks whether categories are displayed correctly when present.
    '''
    def test_explore_view_with_languages(self):
        add_language('Spanish', 'this-be-a-slug', "https://i.kym-cdn.com/photos/images/newsfeed/001/688/970/a72.jpg")
        response = self.client.get(reverse('lanex:explore'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spanish")

        num_categories = len(response.context['languages'])
        self.assertEquals(num_categories, 1)


    def test_location_explore(self):
        """
        Tests to see that view location matches  expected url written into url search bar by users  (hardcoded)'
        """
        response = self.client.get('/explore/')
        self.assertEqual(response.status_code, 200)


    """
    Tests to see that the anticipated relative view is able to call upon the index view. 
    """
    def test_url_accessibility(self):
        response = self.client.get(reverse('lanex:explore'))
        self.assertEquals(response.status_code, 200)


class ShowUserProfileViewTesting(TestCase):
    """
    Test to see that passing username to the relative view invokes the user view
    """
    def test_username_parameter(self):
        login = self.client.login(username="ausername", password="apassword4me")
        response = self.client.get(reverse('lanex:show_user', args=("testing",)))
        self.assertEqual(response.status_code, 200)


    '''
    Tests to check that the user view uses its respective template.
    '''
    def test_template_matches(self):
        login = self.client.login(username="ausername", password="apassword4me")
        response = self.client.get(reverse('lanex:show_user', args=("testing",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lanex/user.html")


    """
    Tests that the show_profile view is able to be retrieved by the expected hardcoded url.
    """
    def test_location(self):
        login = self.client.login(username="ausername", password="apassword4me")
        response = self.client.get('/user/testingsomeuser/')
        self.assertEqual(response.status_code, 200)


'''
Tests for the show language view.
'''
class ShowLanguageViewTesting(TestCase):
    """
    Tests to see that when passing the language slug as a view parameter the language view works.
    """                         
    def test_slug_parameter(self):
        slug = "this-be-a-slug"
        language = lanex.models.Language.objects.get_or_create(slug=slug)
        response = self.client.get(reverse('lanex:show_language', args=(slug,)))
        self.assertEqual(response.status_code, 200)


    '''
    Tests to check that the language view uses its respective template.
    '''
    def test_template_matches(self):
        slug = "this-be-a-slug"
        language = lanex.models.Language.objects.get_or_create(slug=slug)
        response = self.client.get(reverse('lanex:show_language', args=(slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lanex/language.html')


    '''
    Tests that the view is able to be invoked by the expected hardcoded url.
    '''
    def test_location(self):
        slug = "this-be-a-slug"
        response = self.client.get('/language/'+slug+'/')
        self.assertEqual(response.status_code, 200)


'''
Tests for the search view.
'''
class SearchViewTesting(TestCase):
    '''
    Tests to check that the search view uses its respective template.
    '''
    def test_template_matches(self):
        response = self.client.get(reverse("lanex:search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lanex/search/search_input.html")


    '''
    Tests that the view is able to be invoked by the expected hardcoded url.
    '''
    def test_location(self):
        response = self.client.get('/search/?q=alanguagereq4me/')
        self.assertEqual(response.status_code, 200)


'''
Tests for the user authentication
'''
class UserAuthenticationTesting(TestCase):
    """
    Tests that the login view is able to be retrieved by the expected hardcoded url.
    """
    def test_location(self):
        response = self.client.get("/accounts/login/")
        self.assertEquals(response.status_code, 200)


    """
    Tests that the register view is able to be retrieved by the expected hardcoded url.
    """
    def test_location(self):
        response = self.client.get("/accounts/register/")
        self.assertEquals(response.status_code, 200)


'''
Test class for the models.
'''
class ModelsTesting(TestCase):

    def setUp(self):
        language = lanex.models.Language.objects.get_or_create(name='Some language')
        lanex.models.Language.objects.get_or_create(name='Some other language also')
        lanex.models.LanguageRequest.objects.get_or_create(language=language[0], 
                                                           title='Some request title', 
                                                           location='Some location', 
                                                           description='Some request description', 
                                                           views=115, 
                                                           creator=create_user_object())


    '''
    User profile class tests to check model exists in directory with expected attributes and types present.
    '''
    def test_userprofile(self):
        self.assertTrue('UserProfile' in dir(lanex.models))
        user_profile = lanex.models.UserProfile()
        
        sought_attributes = {
            'picture': tempfile.NamedTemporaryFile(suffix=".jpg").name,
            'user': create_user_object(),
        }
        
        sought_types = {
            'picture': models.fields.files.ImageField,
            'user': models.fields.related.OneToOneField,
        }
        
        #Counter which increments if the attribute name matches with the expected
        counter = 0
        
        for attribute in user_profile._meta.fields:
            attribute_name = attribute.name
        
            for sought_attribute_name in sought_attributes.keys():
                if sought_attribute_name == attribute_name:
                    counter += 1
                    self.assertEqual(type(attribute), sought_types[attribute_name], 
                                        f"Attribute type for {attribute_name} = {type(attribute)}; (expected type = {sought_types[attribute_name]})")
                    setattr(user_profile, attribute_name, sought_attributes[attribute_name])

        self.assertEqual(counter, len(sought_attributes.keys()), 
                        f"User profile has {counter} attributes; (expected {len(sought_attributes.keys())})")
        user_profile.save()


    '''
    Tests for the language class model. 
    '''
    def test_language(self):
        language = lanex.models.Language.objects.get(name='Some language')
        self.assertEqual(language.name, 'Some language', "Language model testing failed; (name attribute expected)")
        language = lanex.models.Language.objects.get(name='Some other language also')
        self.assertEqual(language.name, 'Some other language also', "Language model testing failed; (name attribute expected)")

    
    '''
    Tests for the request class model.
    '''
    def test_request_class(self):
        language = lanex.models.Language.objects.get(name='Some language')
        request = lanex.models.LanguageRequest.objects.get(title='Some request title')
        
        self.assertEqual(request.language, language, "Language request model testing failed; (language attribute expected)")
        self.assertEqual(request.title, 'Some request title', "Language request model testing failed; (title attribute expected)")
        self.assertEqual(request.views, 115, "Language request model testing failed; (views attribute expected)")
        self.assertEqual(request.location, 'Some location', "Language request model testing failed; (location attribute expected)")


    '''
    Tests for the string method in models
    '''
    def test_str_method(self):
        language = lanex.models.Language.objects.get(name='Some language')
        request = lanex.models.LanguageRequest.objects.get(title='Some request title')
        
        self.assertEqual(str(language), 'Some language', "Language model string method failed.")
        self.assertEqual(str(request), 'Some request title', "Language request model string method failed.")


'''
Tests for the forms
'''
class FormTests(TestCase):
    
    '''
    Tests to check request form exists in directory with expected form fields present for adding 
      language requests along with fields being of expected types and names match with 
      the ones existing in the request form.
    '''
    def test_request_form(self):
        self.assertTrue('RequestForm' in dir(forms))
        request_form = forms.RequestForm()
        fields = request_form.fields
        
        sought_fields = {
            'language': django_field_models.ModelChoiceField,
            'title': django_fields.CharField,
            'description': django_fields.CharField,
            'views': django_fields.IntegerField,
            'suggested_date' : django_fields.DateTimeField,
            'city': django_fields.CharField,
            'location': PlainLocationField,
        }
        
        for sought_field_name in sought_fields:
            sought_field = sought_fields[sought_field_name]
            self.assertTrue(sought_field_name in fields.keys(), 
                            f"Could not find {sought_field_name} in request form.")
            self.assertEqual(sought_field, type(fields[sought_field_name]), 
                            f"The field {sought_field_name} of type {type(fields[sought_field_name])} in the request form is of an improper type; ({sought_field} expected)")


    '''
    Tests to check user settings forms exists in directory with expected form fields present for 
      the user account account parameters filled in along with fields being of expected types. Fields
      included for example are the user's full name and email, and profile image.
    '''
    def test_user_settings_form(self):
        self.assertTrue('UserFormAdditional' in dir(forms))
        self.assertTrue('UserProfileForm' in dir(forms))
        
        user_form = forms.UserFormAdditional()
        user_profile_form = forms.UserProfileForm()
        
        sought_user_fields = {
            'email': django_fields.EmailField,
            'first_name': django_fields.CharField,
            'last_name': django_fields.CharField,
        }
        
        sought_profile_fields = {
            'picture': django_fields.ImageField,
        }
        
        fields = user_form.fields
        
        for sought_field_name in sought_user_fields:
            sought_field = sought_user_fields[sought_field_name]
            self.assertTrue(sought_field_name in fields.keys(), f"User settings form does not contain the field {sought_field_name}.")
            self.assertEqual(sought_field, type(fields[sought_field_name]), f"The field {sought_field_name} of type {type(fields[sought_field_name])} in the user settings form is of an improper type; ({sought_field} expected)")
        
        fields = user_profile_form.fields
        for sought_field_name in sought_profile_fields:
            sought_field = sought_profile_fields[sought_field_name]
            self.assertTrue(sought_field_name in fields.keys(), f"Failed to retrieve from user settings form the field named {sought_field_name}.")
            self.assertEqual(sought_field, type(fields[sought_field_name]), f"The field {sought_field_name} of type {type(fields[sought_field_name])} in the user settings form is of an improper type; ({sought_field} expected)")


'''
Testing the population script: 
  Checks if the module successfully imports, that the function to populate the script inside the
  module is present and, if unsuccessful, throws appropriate exceptions.
  If all goes fine, proceeds to call the populate function.
'''
class ScriptTesting(TestCase):

    def setUp(self):
        try:
            import populate_lanex
        except ImportError:
            raise ImportError("Failed to import the population script.")
        
        if 'populate' not in dir(populate_lanex):
            raise NameError('Missing the functiion to populate the script.')
        populate_lanex.populate()


    '''
    Testing that the anticipated languages were created without issue.
    Uses a map method to convert language objects into string format for -in- comparisons,
      taking advantage of the iterator created to help with the conversions. 
    '''

    def test_languages(self):
        languages = lanex.models.Language.objects.filter()
        languages_as_strings = map(str, languages)
        
        self.assertEqual(len(languages), 5, "Five languages were anticipated.")
        self.assertTrue('French' in languages_as_strings, "Although the language of French was expected, it seems to not exist.")
        self.assertTrue('Spanish' in languages_as_strings, "Although the language of Spanish was expected, it seems to not exist.")
        self.assertTrue('Japanese' in languages_as_strings, "Although the language of Japanese was expected, it seems to not exist.")
        self.assertTrue('English' in languages_as_strings, "Although the language of English was expected, it seems to not exist.")
        self.assertTrue('Others' in languages_as_strings, "Although some language inside Others was expected, it seems nothing for it was created.")


    '''
    Testing to check that requests (created with users entering in the form which language they are
      interested in) are created without issue. This includes the four main languages and the
      Others category for languages not covered but some users may like to create requests for.
    '''
    def test_requests(self):
        requests_information = {
            'French': ['A French-English study group sounds good', 'Nous sommes des gamers [FR/EN Gamer Squad]', 'Ici, we speak about One Piece - and we do it in Frenglish'],
            'Spanish': ['Saludos', 'Female Spanish-English reading club in Texas', 'Holaaaa'],
            'Japanese': ['魔道士', 'hello O_O Japanese friends', 'I do not have a good title [Norwegian wanting to learn Japanese ^^]'],
            'English': ['Interested in practising with English natives', 'Hallo meine Freunde, guten Tag euch allen (ahem hi)', 'What is up tout le monde, comment va-ton ?'],
            'Others': ['Привет классные люди', 'Ciao! Hey there! السلام عليكم', 'Hi, hi, hi! 大家好 ！！！'],
        }
        
        for language in requests_information:
            request_titles = requests_information[language]
            self.check_add_language_requests(language, request_titles)


    '''
    Method helping to check for proper added language requests and matches correct with what is
      expected.
    '''
    
    def check_add_language_requests(self, language, request_titles):
        language = lanex.models.Language.objects.get(name=language)
        requests = lanex.models.LanguageRequest.objects.filter(language=language)
        self.assertEqual(len(requests), len(request_titles), f"Actual number of requests {len(requests)} does not match with expected {len(request_titles)}")
        
        for title in request_titles:
            try:
                request_title = lanex.models.LanguageRequest.objects.get(title=title)
            except lanex.models.LanguageRequest.DoesNotExist:
                raise ValueError(f"Couldn't find title {title} for the language {language}")
            self.assertEqual(request_title.language, language)
