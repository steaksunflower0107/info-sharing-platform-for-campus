from django.shortcuts import render, HttpResponse, redirect
# Create your views here.
from app01.myForms import MyRegForm
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required


# from django.db.models import Count
# from django.db.models.functions import TruncMonth


def register(request):
    form_obj = MyRegForm()
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        # 判断数据是否合法
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            # 将字典里的confirm_password键值对删除
            clean_data.pop('confirm_password')
            # 用户头像
            file_obj = request.FILES.get('avatar')
            '''
            针对用户头像，一定要判断是否传值，不能直接添加到字典中去
            '''
            if file_obj:
                clean_data['avatar'] = file_obj
            # 直接操作数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)

    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'massage': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')

        # 先校验验证码是否正确
        if request.session.get('code').upper() == code.upper():
            # 校验用户名和密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)

            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['massage'] = '用户名或密码错误'

        else:
            back_dic['code'] = 3000
            back_dic['massage'] = '验证码错误'
        return JsonResponse(back_dic)

    return render(request, 'login.html')


'''
图片相关的模块
    pip install pillow
'''

from PIL import Image, ImageDraw, ImageFont

'''
Image:生成图片 
ImageDraw:能够在图片上进行操作
ImageFont:用来控制字体样式
'''
from io import BytesIO

'''
内存管理器模块
BytesIO: 临时帮助存储数据，返回的时候数据是二进制格式 
StringIO: 临时帮助存储数据，返回的时候数据是字符串格式 
'''
import random


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    # 利用pillow模块动态的产生图片
    # img_obj = Image.new('RGB', (430, 35), 'red')
    img_obj = Image.new('RGB', (430, 35), get_random())
    # 将图片对象保存
    # 将图片对象读取出来
    # 借助于内存管理器模块
    # io_obj = BytesIO()  # 生成一个内存管理器对象
    # img_obj.save(io_obj, 'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存管理器中读取二进制的数据返回给前端

    # 写图片验证码
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/111.ttf', 30)  # 字体样式 大小

    # 随机验证码(五位数，包含数字、小写字母、大写字母)
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 每次循环从上面三个中随机选择一个
        temp = random.choice([random_lower, random_upper, random_int])
        # 将随机产生的字符串写入到图片上
        img_draw.text((i * 90, 0), temp, get_random(), img_font)
        # 记录拼接后的字符串
        code += temp

    # 随机验证码在登录的视图函数中需要用到，要比对，所以要找地方存起来并且要让其他视图函数也能拿到
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    # 查询本网站所有的文章数据并展示到前端页面，使用分页器做分页
    article_queryset = models.Article.objects.all()
    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'massage': ''}
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            old_password = request.POST.get('old_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['massage'] = '修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['massage'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['massage'] = '原密码校对错误'
        return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    redirect('/home/')


@login_required
def site(request, username, **kwargs):
    '''
    :param request:
    :param username:
    :param kwargs:  如果该参数有值，也就意味着需要对article_list做额外的筛选操作
    :return:
    '''
    # 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 用户如果不存在应该返回一个404页面
    if not user_obj:
        return render(request, 'errors.html')

    blog = user_obj.blog
    # 查询当前个人站点下所有的文章
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')

        # 判断用户想按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tag__id=param)
        elif condition == 'archive':
            year, month = param.split('-')  # 2022-12 [2022,12]
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    # 1.查询当前用户所有的分类及分类下的文章数
    # category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
    # 2.查询当前用户所有的标签及标签下的文章数
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(
    #                             count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
    # 3.按照年、月统计所有的文章并分组
    # date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')

    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()

    if not article_obj:
        return render(request, 'errors.html')

    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


import json
from django.db.models import F


def up_or_down(request):
    '''
    1.校验用户是否登录
    2.当前用户是否给自己点赞点踩，自己不能点自己的文章
    3.当前用户是否已经给当前用户点过了
    4.操作数据库
    :param request:
    :return:
    '''
    if request.is_ajax():
        back_dic = {'code': 1000, 'massage': ''}
        # 判断当前用户是否登录
        if request.user.is_authenticated():
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('isUp')  # json传过来是一个布尔值类型
            is_up = json.loads(is_up)  # 转换成布尔值

            # 判断当前文章是否是用户自己写的
            # 根据文章id查文章对象，根据文章对象查作者，根据request.user比对
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 校验当前用户是否已经点过了
                is_click = models.UpAndDown.objects.filter(user=request.user, article=article_id)
                if not is_click:
                    # 操作数据库     要同步操作普通字段
                    # 判断用户点了赞还是踩，从而决定给哪个字段加一
                    if is_up:
                        # 给点赞数加1
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['massage'] = '点赞成功'
                    else:
                        models.Article.objects.filter(pk=article_id).update(down_num=F('up_num') + 1)
                        back_dic['massage'] = '点踩成功'
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1001
                    back_dic['massage'] = '您已经点过了'
            else:
                back_dic['code'] = 1002
                back_dic['massage'] = '不可以给自己点赞点踩哦~'
        else:
            back_dic['code'] = 1003
            back_dic['massage'] = '<a href="/login/">请先登录哦~</a>'

        return JsonResponse(back_dic)


from django.db import transaction


def comment(request):
    '''
    自己也可以评论自己的文章
    :param request:
    :return:
    '''
    if request.is_ajax():
        back_dic = {'code': 1000, 'massage': ''}

        if request.method == 'POST':
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                # 操作评论表，存储数据    两张表
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content, parent_id=parent_id)
                back_dic['massage'] = '评论成功'

            else:
                back_dic['code'] = 1001
                back_dic['massage'] = '用户未登录'

        return JsonResponse(back_dic)


from utils.mypage import Pagination
@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count(), per_page_num=10)
    page_queryset = article_list[page_obj.start:page_obj.end]

    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup
@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')

        # bs4使用
        soup = BeautifulSoup(content, 'html.parser')
        # 获取所有的标签
        tags = soup.find_all()
        for tag in tags:
            # 针对script直接删除
            tag.decompose()

        # 文章简介
        #   先切去content前150个字符
        # desc = content[0:150]
        desc = soup.text[0:150]
        article_obj = models.Article.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog,
        )
        # 文章和标签的关系表是自己创建的，不能用add、set等方法
        # 手动操作关系表  使用批量插入bulk_create
        article_obj_list = []
        for i in tag_id_list:
            # 生成对象并加入到列表
            article_obj_list.append(models.ArticleToTag(article=article_obj, tag_id=i))
            # 批量插入数据
        models.ArticleToTag.objects.bulk_create(article_obj_list)
        # 跳转到后台管理文章展示页
        return redirect('/backend/')

    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)

    return render(request, 'backend/add_article.html', locals())


import os
from bbs_cnblogs import settings
def upload_img(request):
    # 用户写文章上传的图片为静态资源，也应放到防盗media文件夹下
    back_dic = {'error': 0}  # 定义返回给编辑器的数据格式
    if request.method == 'POST':
        # 获取用户上传的图片对象
        file_obj = request.FILES.get('imgFile')
        # 手动拼接存储文件的路径
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        # 优化操作，判断当前文件夹是否存在，不存在则自动创建
        if not os.path.isdir(file_dir):
            os.mkdir(file_obj)     # 创建一层目录结构
        # 拼接图片的完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = f'/media/article_img/{file_obj.name}'

    return JsonResponse(back_dic)

@login_required()
def set_avatar(request):
    print(11111)
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)  # 不会加avatar前缀
        # 手动加前缀
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        return redirect('/home/')
    blog = request.user.blog
    username = request.user.username
    return render(request, 'set_avatar.html', locals())