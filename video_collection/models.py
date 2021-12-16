from urllib import parse
from django.core.exceptions import ValidationError
from django.db import models

class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    #blank=True allows user to enter a note without a name, null=True allows null values
    video_id = models.CharField(max_length=40, unique=True)

    # overriding the save method

    def save(self, *args, **kwargs):
        try:  # add try except to catch possible ValueError
            # extracting id from youtube url
            url_components = parse.urlparse(self.url)
            
            if url_components.scheme != 'https':
                # checks that https is part of url_components
                raise ValidationError(f'Not a youtube url {self.url}')
            if url_components.netloc != 'www.youtube.com':
                # checks that net location is youtube
                raise ValidationError(f'Not a youtube url {self.url}')
            if url_components.path != '/watch':
                raise ValidationError(f'Not a youtube url {self.url}')
            
            query_string = url_components.query
            if not query_string:
                raise ValidationError(f'Invalid youtube url {self.url}')
            parameters = parse.parse_qs(query_string, strict_parsing=True)
            # makes a dictionary out of list from id- the v= from video
            v_parameters_list = parameters.get('v')
            # will return none if key not found
            if not v_parameters_list:
                # if not None or empty
                raise ValidationError(f'Invalid youtube url, missing parameters {self.url}')
            self.video_id = v_parameters_list[0]
        except ValueError as e:
            # Catch the ValueError that may be thrown from 
            # parse.urlparse, if the url is not a valid url,
            # then throw a ValidationError. All invalid data 
            # in the model - missing name for example - 
            # will cause ValidationError, so it's easy for the 
            # view to check for any and all validation errors, 
            # they all cause the same type of exception. 
            raise ValidationError(f'Unable to parse URL {self.url}') from e
        
        super().save(*args, **kwargs)
        # calling django save method to save

    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID: {self.video_id}, Notes: {self.notes[:200]}'
       