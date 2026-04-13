from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import (
    Coach, Student, CourseSubject, SessionYear,
    Attendance, AttendanceReport, StudentResult,
    LeaveReportCoach, FeedbackCoach, NotificationCoach,
)
import json


@login_required
def coach_home(request):
    coach = Coach.objects.get(admin=request.user)
    subjects = CourseSubject.objects.filter(coach=coach)

    # 我负责的班级里的学员
    class_ids = subjects.values_list('class_level_id', flat=True).distinct()
    total_students = Student.objects.filter(class_level_id__in=class_ids).count()

    # 我的课次考勤统计
    attendances = Attendance.objects.filter(subject__in=subjects)
    total_attendance = AttendanceReport.objects.filter(
        attendance__in=attendances
    ).count()
    attend_present = AttendanceReport.objects.filter(
        attendance__in=attendances, status=True
    ).count()

    # 待处理请假
    pending_leave = LeaveReportCoach.objects.filter(
        coach=coach, leave_status=0
    ).count()

    # 未读通知
    notifications = NotificationCoach.objects.filter(
        coach=coach
    ).order_by('-created_at')[:5]

    context = {
        'page_title': '教练主页',
        'coach': coach,
        'total_students': total_students,
        'total_subjects': subjects.count(),
        'total_attendance': total_attendance,
        'attend_present': attend_present,
        'pending_leave': pending_leave,
        'notifications': notifications,
    }
    return render(request, 'coach_templates/home_content.html', context)


# ── 考勤管理 ──────────────────────────────────

@login_required
def take_attendance(request):
    coach = Coach.objects.get(admin=request.user)
    subjects = CourseSubject.objects.filter(coach=coach)
    sessions = SessionYear.objects.all()
    return render(request, 'coach_templates/take_attendance.html', {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': '记录考勤',
    })


@login_required
def get_students_for_attendance(request):
    """Ajax：根据课程+训练期返回学员列表"""
    subject_id = request.GET.get('subject')
    session_id = request.GET.get('session')
    try:
        subject = CourseSubject.objects.get(id=subject_id)
        students = Student.objects.filter(
            class_level=subject.class_level,
            session_year_id=session_id,
        )
        # 检查今天是否已记录
        import datetime
        today = datetime.date.today()
        attendance_obj = Attendance.objects.filter(
            subject_id=subject_id,
            attendance_date=today,
            session_year_id=session_id,
        ).first()

        student_data = []
        for s in students:
            status = False
            if attendance_obj:
                report = AttendanceReport.objects.filter(
                    student=s, attendance=attendance_obj
                ).first()
                status = report.status if report else False
            student_data.append({
                'id': s.id,
                'name': s.admin.get_full_name() or s.admin.username,
                'rank': s.current_rank,
                'status': status,
            })
        return JsonResponse({'students': student_data, 'error': False})
    except Exception as e:
        return JsonResponse({'error': True, 'message': str(e)})


@login_required
def save_attendance(request):
    """保存考勤"""
    if request.method != 'POST':
        return redirect('/take_attendance')
    try:
        subject_id = request.POST.get('subject_id')
        session_id = request.POST.get('session_year_id')
        attendance_date = request.POST.get('attendance_date')
        student_ids = request.POST.getlist('student_ids')
        present_ids = request.POST.getlist('present_ids')

        attendance, _ = Attendance.objects.get_or_create(
            subject_id=subject_id,
            attendance_date=attendance_date,
            session_year_id=session_id,
        )
        for sid in student_ids:
            AttendanceReport.objects.update_or_create(
                student_id=sid,
                attendance=attendance,
                defaults={'status': sid in present_ids}
            )
        messages.success(request, f'考勤记录已保存（{attendance_date}）')
    except Exception as e:
        messages.error(request, f'保存失败：{e}')
    return redirect('/take_attendance')


@login_required
def update_attendance(request):
    """查看/修改历史考勤"""
    coach = Coach.objects.get(admin=request.user)
    subjects = CourseSubject.objects.filter(coach=coach)
    sessions = SessionYear.objects.all()
    return render(request, 'coach_templates/update_attendance.html', {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': '修改考勤',
    })


@login_required
def get_attendance_dates(request):
    """Ajax：获取某课程+训练期的所有考勤日期"""
    subject_id = request.GET.get('subject')
    session_id = request.GET.get('session')
    attendances = Attendance.objects.filter(
        subject_id=subject_id,
        session_year_id=session_id,
    ).values('id', 'attendance_date')
    data = [
        {'id': a['id'], 'date': str(a['attendance_date'])}
        for a in attendances
    ]
    return JsonResponse({'dates': data, 'error': False})


@login_required
def get_attendance_students(request):
    """Ajax：获取某次考勤的学员出勤详情"""
    attendance_id = request.GET.get('attendance_id')
    reports = AttendanceReport.objects.filter(
        attendance_id=attendance_id
    ).select_related('student__admin')
    data = [
        {
            'id': r.student.id,
            'name': r.student.admin.get_full_name() or r.student.admin.username,
            'status': r.status,
        }
        for r in reports
    ]
    return JsonResponse({'students': data, 'error': False})


@login_required
def save_update_attendance(request):
    """保存修改后的考勤"""
    if request.method != 'POST':
        return redirect('/update_attendance')
    try:
        attendance_id = request.POST.get('attendance_id')
        present_ids = request.POST.getlist('present_ids')
        reports = AttendanceReport.objects.filter(attendance_id=attendance_id)
        for r in reports:
            r.status = str(r.student.id) in present_ids
            r.save()
        messages.success(request, '考勤修改已保存')
    except Exception as e:
        messages.error(request, f'修改失败：{e}')
    return redirect('/update_attendance')


# ── 成绩管理 ──────────────────────────────────

@login_required
def add_result(request):
    coach = Coach.objects.get(admin=request.user)
    subjects = CourseSubject.objects.filter(coach=coach)
    return render(request, 'coach_templates/add_result.html', {
        'subjects': subjects,
        'page_title': '录入成绩',
    })


@login_required
def get_students_for_result(request):
    """Ajax：根据课程返回学员列表及已有成绩"""
    subject_id = request.GET.get('subject')
    try:
        subject = CourseSubject.objects.get(id=subject_id)
        students = Student.objects.filter(class_level=subject.class_level)
        data = []
        for s in students:
            result = StudentResult.objects.filter(
                student=s, subject=subject
            ).first()
            data.append({
                'id': s.id,
                'name': s.admin.get_full_name() or s.admin.username,
                'rank': s.current_rank,
                'test_score': result.test_score if result else 0,
                'exam_score': result.exam_score if result else 0,
            })
        return JsonResponse({'students': data, 'error': False})
    except Exception as e:
        return JsonResponse({'error': True, 'message': str(e)})


@login_required
def save_result(request):
    if request.method != 'POST':
        return redirect('/add_result')
    try:
        subject_id = request.POST.get('subject_id')
        student_ids = request.POST.getlist('student_ids')
        for sid in student_ids:
            test  = float(request.POST.get(f'test_{sid}', 0))
            exam  = float(request.POST.get(f'exam_{sid}', 0))
            rank  = request.POST.get(f'rank_{sid}', '')
            StudentResult.objects.update_or_create(
                student_id=sid,
                subject_id=subject_id,
                defaults={
                    'test_score': test,
                    'exam_score': exam,
                    'new_rank': rank or None,
                }
            )
            # 如果指定了新段位，同步更新学员档案
            if rank:
                Student.objects.filter(id=sid).update(current_rank=rank)
        messages.success(request, '成绩录入成功')
    except Exception as e:
        messages.error(request, f'录入失败：{e}')
    return redirect('/add_result')


# ── 请假申请 ──────────────────────────────────

@login_required
def coach_apply_leave(request):
    coach = Coach.objects.get(admin=request.user)
    if request.method == 'POST':
        leave_date = request.POST.get('leave_date', '')
        leave_msg  = request.POST.get('leave_message', '').strip()
        if leave_date and leave_msg:
            LeaveReportCoach.objects.create(
                coach=coach,
                leave_date=leave_date,
                leave_message=leave_msg,
            )
            messages.success(request, '请假申请已提交')
            return redirect('/coach_apply_leave')
        messages.error(request, '请填写完整信息')
    leaves = LeaveReportCoach.objects.filter(coach=coach).order_by('-created_at')
    return render(request, 'coach_templates/apply_leave.html', {
        'leaves': leaves,
        'page_title': '请假申请',
    })


# ── 反馈 ──────────────────────────────────────

@login_required
def coach_send_feedback(request):
    coach = Coach.objects.get(admin=request.user)
    if request.method == 'POST':
        feedback = request.POST.get('feedback', '').strip()
        if feedback:
            FeedbackCoach.objects.create(coach=coach, feedback=feedback)
            messages.success(request, '反馈已发送')
            return redirect('/coach_send_feedback')
    feedbacks = FeedbackCoach.objects.filter(coach=coach).order_by('-created_at')
    return render(request, 'coach_templates/send_feedback.html', {
        'feedbacks': feedbacks,
        'page_title': '意见反馈',
    })