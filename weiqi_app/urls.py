from django.urls import path
from . import views, HodViews, CoachViews, StudentViews

urlpatterns = [
    # public
    path('', views.login_page, name='login'),
    path('login', views.login_page),
    path('doLogin', views.do_login, name='doLogin'),
    path('doRegister', views.do_register, name='doRegister'),
    path('logout_user', views.logout_user, name='logout'),

    # admin
    path('admin_home', HodViews.admin_home),
    path('manage_class', HodViews.manage_class),
    path('add_class', HodViews.add_class),
    path('edit_class/<int:class_id>', HodViews.edit_class),
    path('delete_class/<int:class_id>', HodViews.delete_class),
    path('manage_session', HodViews.manage_session),
    path('add_session', HodViews.add_session),
    path('delete_session/<int:session_id>', HodViews.delete_session),
    path('manage_coach', HodViews.manage_coach),
    path('add_coach', HodViews.add_coach),
    path('edit_coach/<int:coach_id>', HodViews.edit_coach),
    path('delete_coach/<int:coach_id>', HodViews.delete_coach),
    path('manage_student', HodViews.manage_student),
    path('add_student', HodViews.add_student),
    path('edit_student/<int:student_id>', HodViews.edit_student),
    path('delete_student/<int:student_id>', HodViews.delete_student),
    path('manage_subject', HodViews.manage_subject),
    path('add_subject', HodViews.add_subject),
    path('delete_subject/<int:subject_id>', HodViews.delete_subject),
    path('student_leave_view', HodViews.student_leave_view),
    path('student_approve_leave/<int:leave_id>', HodViews.student_approve_leave),
    path('coach_leave_view', HodViews.coach_leave_view),
    path('coach_approve_leave/<int:leave_id>', HodViews.coach_approve_leave),
    path('view_student_feedback', HodViews.view_student_feedback),
    path('view_coach_feedback', HodViews.view_coach_feedback),
    path('send_student_notification', HodViews.send_student_notification),
    path('send_coach_notification', HodViews.send_coach_notification),

    # coach
    path('coach_home', CoachViews.coach_home),
    path('take_attendance', CoachViews.take_attendance),
    path('get_students_for_attendance', CoachViews.get_students_for_attendance),
    path('save_attendance', CoachViews.save_attendance),
    path('update_attendance', CoachViews.update_attendance),
    path('get_attendance_dates', CoachViews.get_attendance_dates),
    path('get_attendance_students', CoachViews.get_attendance_students),
    path('save_update_attendance', CoachViews.save_update_attendance),
    path('add_result', CoachViews.add_result),
    path('get_students_for_result', CoachViews.get_students_for_result),
    path('save_result', CoachViews.save_result),
    path('coach_apply_leave', CoachViews.coach_apply_leave),
    path('coach_send_feedback', CoachViews.coach_send_feedback),

    # student
    path('student_home', StudentViews.student_home),
    path('student_view_attendance', StudentViews.student_view_attendance),
    path('get_attendance_student', StudentViews.get_attendance_student),
    path('student_view_result', StudentViews.student_view_result),
    path('student_apply_leave', StudentViews.student_apply_leave),
    path('student_send_feedback', StudentViews.student_send_feedback),
]