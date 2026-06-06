from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

from shop.models import Profile


class Command(BaseCommand):
    help = 'Создаёт группы ролей и профили для существующих пользователей'

    def handle(self, *args, **options):
        for name in ['Покупатель', 'Менеджер', 'Администратор']:
            Group.objects.get_or_create(name=name)
        self.stdout.write('Группы созданы.')

        customer_group = Group.objects.get(name='Покупатель')
        admin_group = Group.objects.get(name='Администратор')

        for user in User.objects.all():
            Profile.objects.get_or_create(user=user)
            if not user.groups.exists():
                if user.is_staff or user.is_superuser:
                    user.groups.add(admin_group)
                else:
                    user.groups.add(customer_group)

        self.stdout.write(self.style.SUCCESS('Готово: профили и группы настроены.'))
