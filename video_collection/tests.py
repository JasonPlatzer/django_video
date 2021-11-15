from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class TestHomePageMessage(TestCase):
    def test_app_title_message_shown_on_homepage(self):
        url = reverse('home')
        # home is from urls.py
        # generates full url
        response = self.client.get(url)
        # you make requests to client
        # response = is request to server
        self.assertContains(response, 'Cat videos')


class TestAddVideos(TestCase):

    def test_add_video(self):
        valid_video = {
            'name': 'more cat',
            'url': 'https://www.youtube.com/watch?v=DHfRfU3XUEo',
            'notes': 'more cat videos'
        }
        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)
        # follow follows redirect from adding a video
        self.assertTemplateUsed('video_collection/video_list.html')
        self.assertContains(response, 'more cat')
        self.assertContains(response, 'more cat videos')
        self.assertContains(response, 'https://www.youtube.com/watch?v=DHfRfU3XUEo')

        video_count = Video.objects.count()
        self.assertEquals(1, video_count)
        # another way of doing it
        video = Video.objects.first()
        # will check if video is added because data is cleared after every run
        self.assertEqual('more cat', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=DHfRfU3XUEo', video.url)
        self.assertEqual('more cat videos', video.notes)
        self.assertEqual('DHfRfU3XUEo', video.video_id)
    
    def test_add_video_invalid_url_not_added(self):
        inavalid_video_urls = [
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://github.com?v=123'


        ]
        for invalid_video_url in inavalid_video_urls:
            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }
            url = reverse('add_video')
            response = self.client.post(url, new_video)

            self.assertTemplateUsed('video_collection/add.html')
            messages = response.context['messages']
            # gets the messages shown when an invalid video is added
            # 'messages' is from views.py
            message_texts = [ message.message for message in messages]
            # gets messages shown on screen
            self.assertIn('Invalid youtube url', message_texts)
            self.assertIn('Please check the data entered', message_texts)

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    
    def test_all_videos_displayed_in_correct_oreder(self):
        v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=125')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=126')
        expected_video_order = [v3, v2, v4, v1]
        url = reverse('video_list')
        response = self.client.get(url)
        videos_in_template = list(response.context['videos'])
        # context is all the data shown with the template, the
        # dictionary rendered from views.py, has videos and a search form
        self.assertEqual(videos_in_template, expected_video_order)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, '2 videos')


class TestVideoSearch(TestCase):
    pass


class TestVideoModel(TestCase):
    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')

    def test_invalid_url_raises_integrity_error(self):
        inavalid_video_urls = [
            'https://www.youtube.com/watch?'
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=112',
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://github.com?v=123'
        ]
        for invalid_video_url in inavalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_video_url, notes='example notes')

        self.assertEqual(0, Video.objects.count())

