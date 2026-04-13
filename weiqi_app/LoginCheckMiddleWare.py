from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info.lstrip('/')

        # 这些路径不拦截
        open_urls = ['', 'login', 'doLogin', 'doRegister', 'admin']
        for url in open_urls:
            if path == url or path.startswith('admin/'):
                return None

        if not request.user.is_authenticated:
            return redirect('/')

        user_type = request.user.user_type

        if user_type == '1':  # 管理员：禁止访问 coach_ / student_ 前缀页面
            blocked = ('coach_home', 'student_home')
            if path in blocked:
                return redirect('/admin_home')

        elif user_type == '2':  # 教练：禁止访问管理员和学员页面
            blocked_prefix = ('admin_', 'manage_', 'add_student',
                              'edit_student', 'student_home')
            if any(path.startswith(p) for p in blocked_prefix):
                return redirect('/coach_home')

        elif user_type == '3':  # 学员：只能访问 student_ 前缀页面
            allowed_prefix = ('student_', 'logout_user',
                              'get_attendance_dates', 'get_attendance_student')
            if not any(path.startswith(p) for p in allowed_prefix):
                return redirect('/student_home')