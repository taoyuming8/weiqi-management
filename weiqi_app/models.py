from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    HOD = '1'
    COACH = '2'
    STUDENT = '3'

    USER_TYPE_CHOICES = (
        (HOD, '管理员'),
        (COACH, '教练'),
        (STUDENT, '学员'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default=HOD,
    )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            try:
                if self.user_type == self.COACH:
                    Coach.objects.get_or_create(admin=self)
                elif self.user_type == self.STUDENT:
                    Student.objects.get_or_create(
                        admin=self,
                        defaults={
                            'gender': '男',
                            'address': '',
                            'class_level': None,
                            'session_year': None,
                            'current_rank': '未定级',
                        }
                    )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f'创建关联档案失败: {e}')


class ClassLevel(models.Model):
    """班级/级别"""
    name = models.CharField(max_length=100, verbose_name='班级名称')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级列表'


class SessionYear(models.Model):
    """训练期/学期"""
    session_start = models.DateField(verbose_name='开始日期')
    session_end = models.DateField(verbose_name='结束日期')

    def __str__(self):
        return f"{self.session_start} ~ {self.session_end}"

    class Meta:
        verbose_name = '训练期'
        verbose_name_plural = '训练期列表'


class Coach(models.Model):
    """教练"""
    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='coach'
    )
    address = models.TextField(verbose_name='地址', blank=True)
    profile_pic = models.FileField(
        upload_to='coach_profiles/', blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.get_full_name() or self.admin.username

    class Meta:
        verbose_name = '教练'
        verbose_name_plural = '教练列表'


class Student(models.Model):
    """学员"""
    RANK_CHOICES = [
        ('未定级', '未定级'),
        ('30K', '30K'), ('25K', '25K'), ('20K', '20K'),
        ('15K', '15K'), ('10K', '10K'), ('5K', '5K'), ('1K', '1K'),
        ('1D', '1段'), ('2D', '2段'), ('3D', '3段'),
        ('4D', '4段'), ('5D', '5段'),
    ]
    GENDER_CHOICES = [('男', '男'), ('女', '女'), ('其他', '其他')]

    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='student'
    )
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES,
        verbose_name='性别', default='男'
    )
    profile_pic = models.FileField(
        upload_to='student_profiles/', blank=True, null=True
    )
    address = models.TextField(verbose_name='地址', blank=True)
    class_level = models.ForeignKey(
        ClassLevel, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='班级'
    )
    session_year = models.ForeignKey(
        SessionYear, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='训练期'
    )
    current_rank = models.CharField(
        max_length=10, choices=RANK_CHOICES,
        default='未定级', verbose_name='当前段位'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.get_full_name() or self.admin.username

    class Meta:
        verbose_name = '学员'
        verbose_name_plural = '学员列表'


class CourseSubject(models.Model):
    """课程科目"""
    name = models.CharField(max_length=100, verbose_name='课程名称')
    class_level = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, verbose_name='所属班级'
    )
    coach = models.ForeignKey(
        Coach, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='负责教练'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}（{self.class_level}）"

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程列表'


class Attendance(models.Model):
    """考勤课次"""
    subject = models.ForeignKey(
        CourseSubject, on_delete=models.CASCADE, verbose_name='课程'
    )
    attendance_date = models.DateField(verbose_name='上课日期')
    session_year = models.ForeignKey(
        SessionYear, on_delete=models.CASCADE, verbose_name='训练期'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} — {self.attendance_date}"

    class Meta:
        verbose_name = '考勤课次'


class AttendanceReport(models.Model):
    """学员考勤明细"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    attendance = models.ForeignKey(
        Attendance, on_delete=models.CASCADE, verbose_name='课次'
    )
    status = models.BooleanField(default=False, verbose_name='是否出勤')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '考勤明细'
        unique_together = ('student', 'attendance')


class StudentResult(models.Model):
    """学员成绩/段位考核"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    subject = models.ForeignKey(
        CourseSubject, on_delete=models.CASCADE, verbose_name='课程'
    )
    test_score = models.FloatField(verbose_name='平时分', default=0)
    exam_score = models.FloatField(verbose_name='考核分', default=0)
    new_rank = models.CharField(
        max_length=10, blank=True, null=True, verbose_name='晋升段位'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '成绩记录'


class LeaveReportStudent(models.Model):
    """学员请假"""
    STATUS_CHOICES = [(0, '待审核'), (1, '已批准'), (-1, '已拒绝')]
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    leave_date = models.CharField(max_length=60, verbose_name='请假日期')
    leave_message = models.TextField(verbose_name='请假原因')
    leave_status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '学员请假'


class LeaveReportCoach(models.Model):
    """教练请假"""
    STATUS_CHOICES = [(0, '待审核'), (1, '已批准'), (-1, '已拒绝')]
    coach = models.ForeignKey(
        Coach, on_delete=models.CASCADE, verbose_name='教练'
    )
    leave_date = models.CharField(max_length=60, verbose_name='请假日期')
    leave_message = models.TextField(verbose_name='请假原因')
    leave_status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '教练请假'


class FeedbackStudent(models.Model):
    """学员反馈"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    feedback = models.TextField(verbose_name='反馈内容')
    feedback_reply = models.TextField(blank=True, null=True, verbose_name='回复')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '学员反馈'


class FeedbackCoach(models.Model):
    """教练反馈"""
    coach = models.ForeignKey(
        Coach, on_delete=models.CASCADE, verbose_name='教练'
    )
    feedback = models.TextField(verbose_name='反馈内容')
    feedback_reply = models.TextField(blank=True, null=True, verbose_name='回复')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '教练反馈'


class NotificationStudent(models.Model):
    """学员通知"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    message = models.TextField(verbose_name='通知内容')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '学员通知'


class NotificationCoach(models.Model):
    """教练通知"""
    coach = models.ForeignKey(
        Coach, on_delete=models.CASCADE, verbose_name='教练'
    )
    message = models.TextField(verbose_name='通知内容')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '教练通知'


# ── 围棋专属扩展 ──────────────────────────────

class GameRecord(models.Model):
    """棋谱记录"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    coach = models.ForeignKey(
        Coach, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='指导教练'
    )
    game_date = models.DateField(verbose_name='对局日期')
    opponent = models.CharField(max_length=100, blank=True, verbose_name='对手')
    sgf_file = models.FileField(
        upload_to='game_records/', blank=True, null=True, verbose_name='棋谱(.sgf)'
    )
    note = models.TextField(blank=True, verbose_name='复盘笔记')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '棋谱记录'


class RankPromotion(models.Model):
    """段位晋级记录"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    from_rank = models.CharField(max_length=10, verbose_name='晋级前')
    to_rank = models.CharField(max_length=10, verbose_name='晋级后')
    promotion_date = models.DateField(verbose_name='晋级日期')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '段位晋级'


class Tournament(models.Model):
    """内部赛事"""
    name = models.CharField(max_length=100, verbose_name='赛事名称')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    description = models.TextField(blank=True, verbose_name='说明')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '赛事'


class TournamentEntry(models.Model):
    """赛事参赛记录"""
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, verbose_name='赛事'
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='学员'
    )
    place = models.IntegerField(blank=True, null=True, verbose_name='名次')
    score = models.IntegerField(default=0, verbose_name='积分')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '参赛记录'
        unique_together = ('tournament', 'student')