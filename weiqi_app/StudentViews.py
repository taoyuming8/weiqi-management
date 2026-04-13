from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import (
    Student, CourseSubject, Attendance, AttendanceReport,
    StudentResult, LeaveReportStudent, FeedbackStudent,
    NotificationStudent,
)


@login_required
def student_home(request):
    student = Student.objects.get(admin=request.user)
    subjects = CourseSubject.objects.filter(
        class_level=student.class_level
    )
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    attend_present   = AttendanceReport.objects.filter(
        student=student, status=True
    ).count()
    attend_absent    = total_attendance - attend_present

    # 出勤率
    rate = round(attend_present / total_attendance * 100) if total_attendance else 0

    # 最新成绩
    results = StudentResult.objects.filter(
        student=student
    ).select_related('subject').order_by('-created_at')[:5]

    # 通知
    notifications = NotificationStudent.objects.filter(
        student=student
    ).order_by('-created_at')[:5]

    context = {
        'page_title': '学员主页',
        'student': student,
        'total_subjects': subjects.count(),
        'total_attendance': total_attendance,
        'attend_present': attend_present,
        'attend_absent': attend_absent,
        'attend_rate': rate,
        'results': results,
        'notifications': notifications,
    }
    return render(request, 'student_templates/home_content.html', context)


@login_required
def student_view_attendance(request):
    student  = Student.objects.get(admin=request.user)
    subjects = CourseSubject.objects.filter(class_level=student.class_level)
    return render(request, 'student_templates/view_attendance.html', {
        'subjects': subjects,
        'page_title': '我的考勤',
    })


@login_required
def get_attendance_student(request):
    """Ajax：学员查看自己某课程的考勤明细"""
    subject_id = request.GET.get('subject')
    student    = Student.objects.get(admin=request.user)
    attendances = Attendance.objects.filter(subject_id=subject_id)
    data = []
    for a in attendances:
        report = AttendanceReport.objects.filter(
            student=student, attendance=a
        ).first()
        data.append({
            'date': str(a.attendance_date),
            'status': report.status if report else False,
        })
    return JsonResponse({'attendance': data, 'error': False})


@login_required
def student_view_result(request):
    student = Student.objects.get(admin=request.user)
    results = StudentResult.objects.filter(
        student=student
    ).select_related('subject').order_by('-created_at')
    return render(request, 'student_templates/view_result.html', {
        'results': results,
        'page_title': '我的成绩',
    })


@login_required
def student_apply_leave(request):
    student = Student.objects.get(admin=request.user)
    if request.method == 'POST':
        leave_date = request.POST.get('leave_date', '')
        leave_msg  = request.POST.get('leave_message', '').strip()
        if leave_date and leave_msg:
            LeaveReportStudent.objects.create(
                student=student,
                leave_date=leave_date,
                leave_message=leave_msg,
            )
            messages.success(request, '请假申请已提交，等待审核')
            return redirect('/student_apply_leave')
        messages.error(request, '请填写完整信息')
    leaves = LeaveReportStudent.objects.filter(
        student=student
    ).order_by('-created_at')
    return render(request, 'student_templates/apply_leave.html', {
        'leaves': leaves,
        'page_title': '请假申请',
    })


@login_required
def student_send_feedback(request):
    student = Student.objects.get(admin=request.user)
    if request.method == 'POST':
        feedback = request.POST.get('feedback', '').strip()
        if feedback:
            FeedbackStudent.objects.create(student=student, feedback=feedback)
            messages.success(request, '反馈已发送')
            return redirect('/student_send_feedback')
    feedbacks = FeedbackStudent.objects.filter(
        student=student
    ).order_by('-created_at')
    return render(request, 'student_templates/send_feedback.html', {
        'feedbacks': feedbacks,
        'page_title': '意见反馈',
    })