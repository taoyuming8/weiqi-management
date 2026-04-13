from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser


def login_page(request):
    return render(request, 'login.html')


def do_login(request):
    if request.method != 'POST':
        return redirect('/')
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    user = authenticate(request, username=username, password=password)
    if user is None:
        messages.error(request, '用户名或密码错误')
        return redirect('/')
    login(request, user)
    if user.user_type == '1':
        return redirect('/admin_home')
    elif user.user_type == '2':
        return redirect('/coach_home')
    elif user.user_type == '3':
        return redirect('/student_home')
    messages.error(request, '账号类型异常')
    return redirect('/')


def do_register(request):
    if request.method != 'POST':
        return redirect('/')
    # test
    print('[POST数据]', dict(request.POST))

    username   = request.POST.get('username', '').strip()
    password   = request.POST.get('password', '').strip()
    password2  = request.POST.get('password2', '').strip()
    email      = request.POST.get('email', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name  = request.POST.get('last_name', '').strip()
    user_type  = request.POST.get('user_type', '3').strip()

    if not username:
        messages.add_message(request, messages.ERROR, '用户名不能为空', extra_tags='register')
        return redirect('/')
    if password != password2:
        messages.add_message(request, messages.ERROR, '两次密码不一致', extra_tags='register')
        return redirect('/')
    if len(password) < 8:
        messages.add_message(request, messages.ERROR, '密码至少8位', extra_tags='register')
        return redirect('/')
    if CustomUser.objects.filter(username=username).exists():
        messages.add_message(request, messages.ERROR, f'用户名「{username}」已被使用', extra_tags='register')
        return redirect('/')

    # 打印调试信息到控制台
    print(f'[注册] username={username} user_type={user_type} email={repr(email)}')

    try:
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
        )
        user.is_active = True
        user.save()
        print(f'[注册成功] id={user.id} is_active={user.is_active} check_pw={user.check_password(password)}')

        role_name = {'1': '管理员', '2': '教练', '3': '学员'}.get(user_type, '用户')
        messages.success(request, f'注册成功！已创建{role_name}账号「{username}」，请登录')
        return redirect('/')
    except Exception as e:
        print(f'[注册失败] {type(e).__name__}: {e}')
        messages.add_message(request, messages.ERROR, f'注册失败：{e}', extra_tags='register')
        return redirect('/')


def logout_user(request):
    logout(request)
    return redirect('/')