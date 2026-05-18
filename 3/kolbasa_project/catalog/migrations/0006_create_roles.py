from django.db import migrations

def create_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Контент-типы для моделей
    kolbasa_ct = ContentType.objects.get_for_model(apps.get_model('catalog', 'Kolbasa'))
    cart_ct = ContentType.objects.get_for_model(apps.get_model('catalog', 'Cart'))
    cartitem_ct = ContentType.objects.get_for_model(apps.get_model('catalog', 'CartItem'))

    def get_or_create_perm(codename, ct, name):
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=ct,
            defaults={'name': name}
        )
        return perm

    # Группа "Товаровед"
    tovaroved, _ = Group.objects.get_or_create(name='Товаровед')
    tovaroved.permissions.add(
        get_or_create_perm('add_kolbasa', kolbasa_ct, 'Can add kolbasa'),
        get_or_create_perm('change_kolbasa', kolbasa_ct, 'Can change kolbasa'),
        get_or_create_perm('delete_kolbasa', kolbasa_ct, 'Can delete kolbasa'),
        get_or_create_perm('view_kolbasa', kolbasa_ct, 'Can view kolbasa'),
    )

    # Группа "Менеджер по продажам"
    manager, _ = Group.objects.get_or_create(name='Менеджер по продажам')
    manager.permissions.add(
        get_or_create_perm('add_cart', cart_ct, 'Can add cart'),
        get_or_create_perm('change_cart', cart_ct, 'Can change cart'),
        get_or_create_perm('delete_cart', cart_ct, 'Can delete cart'),
        get_or_create_perm('view_cart', cart_ct, 'Can view cart'),
        get_or_create_perm('add_cartitem', cartitem_ct, 'Can add cart item'),
        get_or_create_perm('change_cartitem', cartitem_ct, 'Can change cart item'),
        get_or_create_perm('delete_cartitem', cartitem_ct, 'Can delete cart item'),
        get_or_create_perm('view_cartitem', cartitem_ct, 'Can view cart item'),
        get_or_create_perm('view_kolbasa', kolbasa_ct, 'Can view kolbasa'),
    )

class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0005_cart_kolbasa_price_large_opt_kolbasa_price_small_opt_and_more'),
        ('auth', '__latest__'),
        ('contenttypes', '__latest__'),
    ]
    operations = [
        migrations.RunPython(create_roles),
    ]