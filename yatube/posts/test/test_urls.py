import http

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()

SLUG_1 = '1'
SLUG_2 = '2'
GROUP_1 = reverse('posts:group_posts', kwargs={'slug': SLUG_1})
GROUP_2 = reverse('posts:group_posts', kwargs={'slug': SLUG_2})


class StaticURLTests(TestCase):
    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, http.HTTPStatus.OK)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='test_username',
        )
        cls.group = Group.objects.create(
            title='заголовок',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='текст проверки теста,.:%;',
            group=cls.group,
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ),
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_for_all_users(self):
        urls_and_response_statuses = {
            reverse('posts:index'): http.HTTPStatus.OK,
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }): http.HTTPStatus.OK,
            reverse('posts:group_posts', kwargs={
                'slug': self.group.slug}): http.HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): http.HTTPStatus.OK,
            '/pagenotfound/': http.HTTPStatus.NOT_FOUND,
        }

        for urls, statuses in urls_and_response_statuses.items():
            with self.subTest(urls=urls):
                response = self.client.get(urls)
                self.assertEqual(response.status_code, statuses)
