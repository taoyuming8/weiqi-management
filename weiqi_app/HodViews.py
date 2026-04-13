from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    CustomUser, Coach, Student, ClassLevel, SessionYear,
    CourseSubject, Attendance, AttendanceReport,
    LeaveReportStudent, LeaveReportCoach,
    FeedbackStudent, FeedbackCoach,
    NotificationStudent, NotificationCoach,
)
import json


@login_required
def admin_home(request):
    student_count = Student.objects.count()
    coach_count = Coach.objects.count()
    class_count = ClassLevel.objects.count()
    subject_count = CourseSubject.objects.count()
    total_attendance = AttendanceReport.objects.count()
    attend_present = AttendanceReport.objects.filter(status=True).count()
    pending_leave_student = LeaveReportStudent.objects.filter(leave_status=0).count()
    pending_leave_coach = LeaveReportCoach.objects.filter(leave_status=0).count()

    # 各班级学员数（用于图表）
    classes = ClassLevel.objects.all()
    class_names = [c.name for c in classes]
    class_student_counts = [
        Student.objects.filter(class_level=c).count() for c in classes
    ]

    context = {
        'page_title': '管理员首页',
        'student_count': student_count,
        'coach_count': coach_count,
        'class_count': class_count,
        'subject_count': subject_count,
        'total_attendance': total_attendance,
        'attend_present': attend_present,
        'pending_leave': pending_leave_student + pending_leave_coach,
        'class_names_json': json.dumps(class_names, ensure_ascii=False),
        'class_counts_json': json.dumps(class_student_counts),
    }
    return render(request, 'hod_templates/home_content.html', context)


# ── 班级管理 ──────────────────────────────────

@login_required
def manage_class(request):
    classes = ClassLevel.objects.all()
    return render(request, 'hod_templates/manage_class.html', {
        'classes': classes, 'page_title': '班级管理'
    })


@login_required
def add_class(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, '班级名称不能为空')
        elif ClassLevel.objects.filter(name=name).exists():
            messages.error(request, '该班级已存在')
        else:
            ClassLevel.objects.create(name=name)
            messages.success(request, f'班级「{name}」添加成功')
            return redirect('/manage_class')
    return render(request, 'hod_templates/add_class.html', {'page_title': '添加班级'})


@login_required
def edit_class(request, class_id):
    obj = ClassLevel.objects.get(id=class_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            obj.name = name
            obj.save()
            messages.success(request, '班级更新成功')
            return redirect('/manage_class')
    return render(request, 'hod_templates/edit_class.html', {
        'class': obj, 'page_title': '编辑班级'
    })


@login_required
def delete_class(request, class_id):
    ClassLevel.objects.filter(id=class_id).delete()
    messages.success(request, '班级已删除')
    return redirect('/manage_class')


# ── 训练期管理 ────────────────────────────────

@login_required
def manage_session(request):
    sessions = SessionYear.objects.all()
    return render(request, 'hod_templates/manage_session.html', {
        'sessions': sessions, 'page_title': '训练期管理'
    })


@login_required
def add_session(request):
    if request.method == 'POST':
        start = request.POST.get('session_start')
        end = request.POST.get('session_end')
        if start and end:
            SessionYear.objects.create(session_start=start, session_end=end)
            messages.success(request, '训练期添加成功')
            return redirect('/manage_session')
        messages.error(request, '请填写完整日期')
    return render(request, 'hod_templates/add_session.html', {'page_title': '添加训练期'})


@login_required
def delete_session(request, session_id):
    SessionYear.objects.filter(id=session_id).delete()
    messages.success(request, '训练期已删除')
    return redirect('/manage_session')


# ── 教练管理 ──────────────────────────────────

@login_required
def manage_coach(request):
    coaches = Coach.objects.select_related('admin').all()
    return render(request, 'hod_templates/manage_coach.html', {
        'coaches': coaches, 'page_title': '教练管理'
    })


@login_required
def add_coach(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '').strip()
        address    = request.POST.get('address', '').strip()

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        else:
            try:
                user = CustomUser.objects.create_user(
                    username=username, password=password,
                    email=email, first_name=first_name,
                    last_name=last_name, user_type='2'
                )
                user.coach.address = address
                if request.FILES.get('profile_pic'):
                    user.coach.profile_pic = request.FILES['profile_pic']
                user.coach.save()
                messages.success(request, f'教练「{first_name}{last_name}」添加成功')
                return redirect('/manage_coach')
            except Exception as e:
                messages.error(request, f'添加失败：{e}')

    return render(request, 'hod_templates/add_coach.html', {'page_title': '添加教练'})


@login_required
def edit_coach(request, coach_id):
    coach = Coach.objects.select_related('admin').get(id=coach_id)
    if request.method == 'POST':
        coach.admin.first_name = request.POST.get('first_name', '')
        coach.admin.last_name  = request.POST.get('last_name', '')
        coach.admin.email      = request.POST.get('email', '')
        coach.address          = request.POST.get('address', '')
        if request.FILES.get('profile_pic'):
            coach.profile_pic = request.FILES['profile_pic']
        coach.admin.save()
        coach.save()
        messages.success(request, '教练信息已更新')
        return redirect('/manage_coach')
    return render(request, 'hod_templates/edit_coach.html', {
        'coach': coach, 'page_title': '编辑教练'
    })


@login_required
def delete_coach(request, coach_id):
    coach = Coach.objects.get(id=coach_id)
    coach.admin.delete()
    messages.success(request, '教练已删除')
    return redirect('/manage_coach')


# ── 学员管理 ──────────────────────────────────

@login_required
def manage_student(request):
    students = Student.objects.select_related('admin', 'class_level').all()
    return render(request, 'hod_templates/manage_student.html', {
        'students': students, 'page_title': '学员管理'
    })


@login_required
def add_student(request):
    classes  = ClassLevel.objects.all()
    sessions = SessionYear.objects.all()
    if request.method == 'POST':
        first_name     = request.POST.get('first_name', '').strip()
        last_name      = request.POST.get('last_name', '').strip()
        username       = request.POST.get('username', '').strip()
        email          = request.POST.get('email', '').strip()
        password       = request.POST.get('password', '').strip()
        gender         = request.POST.get('gender', '男')
        address        = request.POST.get('address', '').strip()
        class_id       = request.POST.get('class_id')
        session_id     = request.POST.get('session_year_id')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        else:
            try:
                user = CustomUser.objects.create_user(
                    username=username, password=password,
                    email=email, first_name=first_name,
                    last_name=last_name, user_type='3'
                )
                user.student.gender         = gender
                user.student.address        = address
                user.student.class_level_id = class_id
                user.student.session_year_id = session_id
                if request.FILES.get('profile_pic'):
                    user.student.profile_pic = request.FILES['profile_pic']
                user.student.save()
                messages.success(request, f'学员「{first_name}{last_name}」添加成功')
                return redirect('/manage_student')
            except Exception as e:
                messages.error(request, f'添加失败：{e}')

    return render(request, 'hod_templates/add_student.html', {
        'classes': classes, 'sessions': sessions, 'page_title': '添加学员'
    })


@login_required
def edit_student(request, student_id):
    student  = Student.objects.select_related('admin').get(id=student_id)
    classes  = ClassLevel.objects.all()
    sessions = SessionYear.objects.all()
    if request.method == 'POST':
        student.admin.first_name  = request.POST.get('first_name', '')
        student.admin.last_name   = request.POST.get('last_name', '')
        student.admin.email       = request.POST.get('email', '')
        student.gender            = request.POST.get('gender', '男')
        student.address           = request.POST.get('address', '')
        student.class_level_id    = request.POST.get('class_id')
        student.session_year_id   = request.POST.get('session_year_id')
        student.current_rank      = request.POST.get('current_rank', '未定级')
        if request.FILES.get('profile_pic'):
            student.profile_pic = request.FILES['profile_pic']
        student.admin.save()
        student.save()
        messages.success(request, '学员信息已更新')
        return redirect('/manage_student')
    return render(request, 'hod_templates/edit_student.html', {
        'student': student, 'classes': classes,
        'sessions': sessions, 'page_title': '编辑学员'
    })


@login_required
def delete_student(request, student_id):
    student = Student.objects.get(id=student_id)
    student.admin.delete()
    messages.success(request, '学员已删除')
    return redirect('/manage_student')


# ── 课程管理 ──────────────────────────────────

@login_required
def manage_subject(request):
    subjects = CourseSubject.objects.select_related('class_level', 'coach').all()
    return render(request, 'hod_templates/manage_subject.html', {
        'subjects': subjects, 'page_title': '课程管理'
    })


@login_required
def add_subject(request):
    classes = ClassLevel.objects.all()
    coaches = Coach.objects.select_related('admin').all()
    if request.method == 'POST':
        name     = request.POST.get('name', '').strip()
        class_id = request.POST.get('class_id')
        coach_id = request.POST.get('coach_id')
        if name and class_id:
            CourseSubject.objects.create(
                name=name, class_level_id=class_id, coach_id=coach_id or None
            )
            messages.success(request, f'课程「{name}」添加成功')
            return redirect('/manage_subject')
        messages.error(request, '请填写课程名称并选择班级')
    return render(request, 'hod_templates/add_subject.html', {
        'classes': classes, 'coaches': coaches, 'page_title': '添加课程'
    })


@login_required
def delete_subject(request, subject_id):
    CourseSubject.objects.filter(id=subject_id).delete()
    messages.success(request, '课程已删除')
    return redirect('/manage_subject')


# ── 请假审核 ──────────────────────────────────

@login_required
def student_leave_view(request):
    leaves = LeaveReportStudent.objects.select_related('student__admin').all()
    return render(request, 'hod_templates/student_leave_view.html', {
        'leaves': leaves, 'page_title': '学员请假审核'
    })


@login_required
def student_approve_leave(request, leave_id):
    action = request.GET.get('action', '1')
    LeaveReportStudent.objects.filter(id=leave_id).update(leave_status=int(action))
    messages.success(request, '审核完成')
    return redirect('/student_leave_view')


@login_required
def coach_leave_view(request):
    leaves = LeaveReportCoach.objects.select_related('coach__admin').all()
    return render(request, 'hod_templates/coach_leave_view.html', {
        'leaves': leaves, 'page_title': '教练请假审核'
    })


@login_required
def coach_approve_leave(request, leave_id):
    action = request.GET.get('action', '1')
    LeaveReportCoach.objects.filter(id=leave_id).update(leave_status=int(action))
    messages.success(request, '审核完成')
    return redirect('/coach_leave_view')


# ── 反馈查看 ──────────────────────────────────

@login_required
def view_student_feedback(request):
    feedbacks = FeedbackStudent.objects.select_related('student__admin').all()
    if request.method == 'POST':
        fb_id = request.POST.get('feedback_id')
        reply = request.POST.get('reply', '').strip()
        if fb_id and reply:
            FeedbackStudent.objects.filter(id=fb_id).update(feedback_reply=reply)
            messages.success(request, '回复已发送')
            return redirect('/view_student_feedback')
    return render(request, 'hod_templates/view_student_feedback.html', {
        'feedbacks': feedbacks, 'page_title': '学员反馈'
    })


@login_required
def view_coach_feedback(request):
    feedbacks = FeedbackCoach.objects.select_related('coach__admin').all()
    if request.method == 'POST':
        fb_id = request.POST.get('feedback_id')
        reply = request.POST.get('reply', '').strip()
        if fb_id and reply:
            FeedbackCoach.objects.filter(id=fb_id).update(feedback_reply=reply)
            messages.success(request, '回复已发送')
            return redirect('/view_coach_feedback')
    return render(request, 'hod_templates/view_coach_feedback.html', {
        'feedbacks': feedbacks, 'page_title': '教练反馈'
    })


# ── 通知发送 ──────────────────────────────────

@login_required
def send_student_notification(request):
    students = Student.objects.select_related('admin').all()
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        message    = request.POST.get('message', '').strip()
        if student_id and message:
            NotificationStudent.objects.create(
                student_id=student_id, message=message
            )
            messages.success(request, '通知已发送')
            return redirect('/send_student_notification')
    return render(request, 'hod_templates/send_student_notification.html', {
        'students': students, 'page_title': '发送学员通知'
    })


@login_required
def send_coach_notification(request):
    coaches = Coach.objects.select_related('admin').all()
    if request.method == 'POST':
        coach_id = request.POST.get('coach_id')
        message  = request.POST.get('message', '').strip()
        if coach_id and message:
            NotificationCoach.objects.create(
                coach_id=coach_id, message=message
            )
            messages.success(request, '通知已发送')
            return redirect('/send_coach_notification')
    return render(request, 'hod_templates/send_coach_notification.html', {
        'coaches': coaches, 'page_title': '发送教练通知'
    })