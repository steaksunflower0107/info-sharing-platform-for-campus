from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='手机号', null=True, blank=True)
    '''
     null=True: 数据库中该字段可以为空 
     blank=True: admin后台管理后可以为空
    '''
    # 头像
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.png',
                              verbose_name='用户头像')
    '''
    给avatar字段传文件对象，该文件对象会自动存储在avatar文件，该字段保存的是文件路径
    '''
    create_time = models.DateTimeField(auto_now_add=True)

    # 外键
    blog = models.OneToOneField(to='Blog', null=True)

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.username


class Blog(models.Model):
    site_name = models.CharField(verbose_name='站点名称', max_length=32)
    site_title = models.CharField(verbose_name='站点标题', max_length=32)
    site_theme = models.CharField(verbose_name='站点样式', max_length=64)    # 存css或js文件路径

    class Meta:
        verbose_name_plural = '博客表'

    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(verbose_name='文章分类', max_length=32)
    # 外键
    blog = models.ForeignKey(to='Blog', null=True)

    class Meta:
        verbose_name_plural = '分章分类表'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='文章标签', max_length=32)
    # 外键
    blog = models.ForeignKey(to='Blog', null=True)

    class Meta:
        verbose_name_plural = '标签表'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(verbose_name='文章标题', max_length=64)
    desc = models.CharField(verbose_name='文章简介', max_length=255)
    content = models.TextField(verbose_name='文章内容')     # text不需要指定最大长度
    create_time = models.DateField(auto_now_add=True)
    # 数据库字段设计优化
    up_num = models.BigIntegerField(verbose_name='点赞数', default=0)
    down_num = models.BigIntegerField(verbose_name='点踩数', default=0)
    comment_num = models.BigIntegerField(verbose_name='评论数', default=0)

    # 外键
    blog = models.ForeignKey(to='Blog', null=True)
    category = models.ForeignKey(to='Category', null=True)
    tag = models.ManyToManyField(to='Tag',
                                 through='ArticleToTag',
                                 through_fields=('article', 'tag')
                                 )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '文章表'


class ArticleToTag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')

    class Meta:
        verbose_name_plural = '文章与标签的对应表'


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField(verbose_name='是否点赞')   # 传布尔值存0/1

    class Meta:
        verbose_name_plural = '点赞点踩表'


class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(verbose_name='评论内容', max_length=255)
    comment_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    # 自关联
    parent = models.ForeignKey(to='self', null=True)    # 有些评论就是根评论

    class Meta:
        verbose_name_plural = '评论表'
