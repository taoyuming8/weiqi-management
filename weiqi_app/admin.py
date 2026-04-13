from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Coach, Student, ClassLevel, SessionYear,
    CourseSubject, Attendance, AttendanceReport,
    StudentResult, LeaveReportStudent, LeaveReportCoach,
    FeedbackStudent, FeedbackCoach,
    NotificationStudent, NotificationCoach,
    GameRecord, RankPromotion, Tournament, TournamentEntry,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter   = ('user_type', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('角色', {'fields': ('user_type',)}),
    )


admin.site.register(Coach)
admin.site.register(Student)
admin.site.register(ClassLevel)
admin.site.register(SessionYear)
admin.site.register(CourseSubject)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(StudentResult)
admin.site.register(LeaveReportStudent)
admin.site.register(LeaveReportCoach)
admin.site.register(FeedbackStudent)
admin.site.register(FeedbackCoach)
admin.site.register(NotificationStudent)
admin.site.register(NotificationCoach)
admin.site.register(GameRecord)
admin.site.register(RankPromotion)
admin.site.register(Tournament)
admin.site.register(TournamentEntry)