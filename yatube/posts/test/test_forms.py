from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TaskCreateFormTests(TestCase):

    def setUp(self):
        self.test_group = Group.objects.create(
            title='тест группа',
            slug='test_slug'
        )
        self.user = User.objects.create(username='test-user')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

    def test_create_post(self):
        """Проверяем что при отправке валидной формы  создания поста
           создаётся новая запись в базе данных"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'тест текст',
            'group': self.test_group.id
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        latest_post = Post.objects.first()
        self.assertEqual(latest_post.text, form_data['text'])
        self.assertEqual(latest_post.author, self.user)
        self.assertEqual(latest_post.group, self.test_group)

    def test_post_edit(self):
        """Проверяем что при отправке  формы со страницы редактирования поста
           происходит изменение поста с post_id в базе данных."""
        post_edit = Post.objects.create(
            author=self.user,
            text='тест текст',
        )
        form_data = {
            'text': 'измененный текст',
        }
        self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': post_edit.id}),
            data=form_data,
            follow=True,
        )
        post_edit.refresh_from_db()
        self.assertEqual(post_edit.text, form_data['text'])
