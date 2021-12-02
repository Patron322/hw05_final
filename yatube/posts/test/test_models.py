from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='тест группа',
            slug='тест слаг',
            description='тест описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовая запись',
        )
        cls.model_str = {
            cls.group: cls.group.title,
            cls.post: cls.post.text[:15],
        }

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает метод __str__."""
        for model, value in self.model_str.items():
            with self.subTest(model=model):
                act = str(model)
                self.assertEqual(act, value)
