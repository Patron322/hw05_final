from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow

User = get_user_model()
SLUG_1 = '1'
SLUG_2 = '2'
GROUP_1 = reverse('posts:group_posts', kwargs={'slug': SLUG_1})
GROUP_2 = reverse('posts:group_posts', kwargs={'slug': SLUG_2})
TEXT_1 = 'text_1'
TEXT_2 = 'text_2'


class TaskViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_p = User.objects.create_user(username='test_author_p')
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title='test-title',
            description='test-description',
        )
        cls.post = Post.objects.create(
            author=cls.author_p,
            text='тестовый текс,ЭЪ/!№;%:?*()',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author_p)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.author_p.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class TaskPaginatorsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username='test_username_a')
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title='test-title',
            description='test-description',
        )
        cls.posts = (Post(text=f'text{i}', author=cls.user_a,
                     group=cls.group) for i in range(13))
        Post.objects.bulk_create(cls.posts, 13)
        cls.name_pages = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': cls.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': cls.user_a.username}
            )
        )

    def setUp(self):
        self.guest_client = Client()

    def test_item_posts_per_page(self):
        for page_name in self.name_pages:
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.guest_client.get(page_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class AnotherGroupTests(TestCase):
    def setUp(self):
        self.author_p = User.objects.create_user(username='test_author_p')
        self.group_1 = Group.objects.create(
            slug='1', title='testtitle1', description='testdesc1'
        )
        self.group_2 = Group.objects.create(
            slug='2', title='testtitle2', description='testdesc2'
        )
        self.post = Post.objects.create(
            author=self.author_p, text=TEXT_1, group=self.group_1)
        self.a_c_author = Client()
        self.a_c_author.force_login(self.author_p)

    def test_post_in_2_group_2(self):
        post2 = Post.objects.create(
            author=self.author_p, text=TEXT_2, group=self.group_2)
        response = self.a_c_author.get(GROUP_1)
        self.assertEqual(response.context['page_obj'][0].id, 1)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        response = self.a_c_author.get(GROUP_2)
        self.assertEqual(response.context['page_obj'][0].id, 2)
        self.assertEqual(response.context['page_obj'][0].text, post2.text)

    def test_index_correct_context(self):
        response = self.a_c_author.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_group_list_correct_context(self):
        response = self.a_c_author.get(
            reverse('posts:group_posts', kwargs={'slug': self.group_1.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.group_1)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_profile_correct_context(self):
        response = self.a_c_author.get(
            reverse('posts:profile',
                    kwargs={'username': self.author_p.username})
        )
        self.assertEqual(response.context['page_obj'][0].author, self.author_p)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(response.context['author'], self.author_p)


class Testsubunsub(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username='test_user_a')
        cls.author_p = User.objects.create_user(username='test_author_p')
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title='test-title',
            description='test-description',
        )

    def setUp(self):
        self.author = User.objects.create(
            username='test_user',
        )
        self.post = Post.objects.create(
            author=self.author,
            text='тестовый текс,ЭЪ/!№;%:?*()',
            group=self.group,
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_user_unsub_and_sub(self):
        user2 = User.objects.create_user(username='test_user2')
        Follow.objects.create(user=self.author_p, author=user2)
        followers_count = Follow.objects.filter(
            user=self.author_p, author=user2
        ).count()
        self.assertEqual(followers_count, 1)
        self.guest_client.get(reverse('posts:profile',
                              kwargs={'username': user2}))
        followers_count = Follow.objects.filter(
            user=self.user_a, author=user2).count()
        self.assertEqual(followers_count, 0)

    def test_follow_post_exists_in_follow_index(self):
        user2 = User.objects.create_user(username='test_user2')
        post = Post.objects.create(text='тест подписки', author=user2)
        Follow.objects.create(user=self.author, author=user2)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post_text1 = response.context['page_obj'][0].text
        self.assertEqual(post.text, post_text1)

    def test_unfollow_post_does_not_exists_in_follow_index(self):
        user2 = User.objects.create_user(username='User2')
        post = Post.objects.create(text='тест подписки', author=user2)
        test_client = Client()
        test_client.force_login(user2)
        Follow.objects.create(user=user2, author=self.author)
        response = test_client.get(reverse('posts:follow_index'))
        post_text1 = response.context['page_obj'][0].text
        self.assertNotEqual(post.text, post_text1)
