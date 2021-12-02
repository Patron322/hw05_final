from django.test import Client, TestCase

from posts.models import Comment, Follow, Group, Post, User

SLUG = 'test-slug'
AUTHOR = 'auth'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'
TEXT1 = 'Тестовый текст'
VERBOSE_FIELD = {
    'text': 'Текст',
    'pub_date': 'Дата',
    'author': 'Автор',
    'group': 'Группа',
}
HELP_FIELD = {
    'text': 'Введите текст поста',
    'group': 'Выберите группу',
}


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.user_2 = User.objects.create_user(
            username='User2'
        )
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT1,
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text=TEXT1,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_2,
            text='text_com'
        )
        cls.follow = Follow.objects.create(
            user=cls.user_2,
            author=cls.user
        )

    def setUp(self):
        self.a_c_author = Client()
        self.a_c_author.force_login(self.user)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        # Проверяем Group
        str_group = self.group
        title_group = self.group.title
        self.assertEqual(title_group, str(str_group))
        # Проверяем Post
        str_post = self.post
        text_post = self.post.text[:15]
        self.assertEqual(text_post, str(str_post))
        # Проверяем Comment
        str_com = self.post
        text_com = self.post.text[:15]
        self.assertEqual(text_com, str(str_com))

    def test_verbose_name(self):
        """Test verbose_name."""
        self.post = PostModelTest.post
        for field, value in VERBOSE_FIELD.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name, value)

    def test_help_text_in_post_model(self):
        """Test help_text."""
        self.post = PostModelTest.post
        for field, value in HELP_FIELD.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, value)

    def test_comment(self):
        """Test comment create."""
        self.assertTrue(Comment.objects.filter(
            text='text_com',
            author=self.user_2).exists())

    def test_follow(self):
        """Test follow."""
        self.assertTrue(Follow.objects.filter(
            user=self.user_2,
            author=self.user).exists())

    def test_unfollow(self):
        self.assertEqual(self.post_2.author.follower.count(), 0)

    def test_uncomment(self):
        self.assertEqual(self.post_2.comments.count(), 0)
