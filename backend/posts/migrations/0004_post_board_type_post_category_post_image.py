# Generated by Django 5.1.3 on 2024-12-03 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_comment_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='board_type',
            field=models.CharField(choices=[('tech', '기술 블로그'), ('free', '자유 게시판'), ('guest', '방명록')], default='free', max_length=10),
        ),
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.CharField(blank=True, choices=[('python', 'Python'), ('javascript', 'JavaScript'), ('java', 'Java'), ('cpp', 'C++'), ('go', 'Go'), ('rust', 'Rust'), ('other', '기타')], help_text='기술 블로그 작성 시 필수 선택', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/%Y/%m/%d/'),
        ),
    ]