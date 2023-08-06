
from django.shortcuts import render_to_response
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from communication.utils import VumiSmsApi
from random import randint
from auth.forms import SendWelcomeSmsForm
from django import template
from communication.utils import get_autologin_link
from auth.models import Learner, SystemAdministrator, SchoolManager,\
    CourseManager, CourseMentor
from .forms import SystemAdministratorChangeForm, \
    SystemAdministratorCreationForm, SchoolManagerChangeForm,\
    SchoolManagerCreationForm, CourseManagerChangeForm, \
    CourseManagerCreationForm, CourseMentorChangeForm, \
    CourseMentorCreationForm, LearnerChangeForm, LearnerCreationForm
import koremutake
from django.contrib.auth.hashers import make_password
from core.models import ParticipantQuestionAnswer
from auth.resources import LearnerResource
from auth.filters import CourseFilter, AirtimeFilter


class SystemAdministratorAdmin(UserAdmin):
    # The forms to add and change user instances
    form = SystemAdministratorChangeForm
    add_form = SystemAdministratorCreationForm

    list_display = ("username", "last_name", "first_name", "country", "area")
    list_filter = ("country", "area")
    search_fields = ("last_name", "first_name", "username")
    ordering = ("country", "area", "last_name")
    filter_horizontal = ()

    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name", "email",
                                      "mobile")}),
        ("Access", {"fields": ("username", "password", "is_active")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("username", "password1",
                               "password2")}),
        ("Region", {"fields": ("country",)})
    )


class SchoolManagerAdmin(UserAdmin):
    # The forms to add and change user instances
    form = SchoolManagerChangeForm
    add_form = SchoolManagerCreationForm

    list_display = ("username", "last_name", "first_name", "country", "area")
    list_filter = ("country", "area")
    search_fields = ("last_name", "first_name", "username")
    ordering = ("country", "area", "last_name")
    filter_horizontal = ()

    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name",
                                      "email", "mobile")}),
        ("Access", {"fields": ("username", "password",
                               "is_active")}),
        ("Region", {"fields": ("country", "area", "city",
                               "school")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("username", "password1",
                               "password2")}),
        ("Region", {"fields": ("country", "area", "school")})
    )


class CourseManagerAdmin(UserAdmin):
    # The forms to add and change user instances
    form = CourseManagerChangeForm
    add_form = CourseManagerCreationForm

    list_display = ("username", "last_name", "first_name", "country", "area")
    list_filter = ("country", "area")
    search_fields = ("last_name", "first_name", "username")
    ordering = ("country", "area", "last_name")
    filter_horizontal = ()

    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name",
                                      "email", "mobile")}),
        ("Access", {"fields": ("username", "password",
                               "is_active")}),
        ("Region", {"fields": ("country", "area", "city",
                               "course")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("username", "password1",
                               "password2")}),
        ("Region", {"fields": ("country", "area", "course")})
    )


class CourseMentorAdmin(UserAdmin):
    # The forms to add and change user instances
    form = CourseMentorChangeForm
    add_form = CourseMentorCreationForm

    list_display = ("username", "last_name", "first_name", "country", "area")
    list_filter = ("country", "area")
    search_fields = ("last_name", "first_name", "username")
    ordering = ("country", "area", "last_name")
    filter_horizontal = ()

    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name",
                                      "email", "mobile")}),
        ("Access", {"fields": ("username", "password",
                               "is_active")}),
        ("Region", {"fields": ("country", "area", "city",
                               "course")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("username", "password1",
                               "password2")}),
        ("Region", {"fields": ("country", "area", "course")})
    )


class LearnerAdmin(UserAdmin, ImportExportModelAdmin):
    # The forms to add and change user instances
    form = LearnerChangeForm
    add_form = LearnerCreationForm
    resource_class = LearnerResource

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ("username", "last_name", "first_name", "school",
                    "area", "completed_questions", "percentage_correct",
                    "welcome_message_sent")
    list_filter = ("first_name", "last_name", "mobile", "country",
                   "area", "welcome_message_sent", CourseFilter, AirtimeFilter)
    search_fields = ("last_name", "first_name", "username")
    ordering = ("country", "area", "last_name")
    filter_horizontal = ()
    readonly_fields = ("mobile",)

    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name",
                                      "email", "mobile")}),
        ("Access", {"fields": ("username", "password",
                               "is_active", "unique_token")}),
        ("Region", {"fields": ("country", "area", "city",
                               "school")}),
        ("Opt-In Communications", {"fields": ("optin_sms", "optin_email")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("username", "password1",
                               "password2")}),
        ("Region", {"fields": ("country", "area", "school")})
    )

    def send_sms(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = SendWelcomeSmsForm(request.POST)

            if form.is_valid():
                vumi = VumiSmsApi()
                message = form.cleaned_data["message"]

                # Check if a password or autologin message
                is_welcome_message = False
                is_autologin_message = False
                if "|password|" in message:
                    is_welcome_message = True
                if "|autologin|" in message:
                    is_autologin_message = True

                successful = 0
                fail = []

                for learner in queryset:
                    password = None
                    if is_welcome_message:
                        # Generate password
                        password = koremutake.encode(randint(10000, 100000))
                        learner.password = make_password(password)
                    if is_autologin_message:
                        # Generate autologin link
                        learner.generate_unique_token()
                    learner.save()

                    # Send sms
                    try:
                        sms, sent = vumi.send(
                            learner.username,
                            message=message,
                            password=password,
                            autologin=get_autologin_link(learner.unique_token)
                        )
                    except:
                        sent = False
                        pass

                    if sent:
                        successful += 1
                    else:
                        fail.append(learner.username)

                    # Save welcome message details
                    if is_welcome_message and sent:
                        learner.welcome_message = sms
                        learner.welcome_message_sent = True

                    learner.save()
                return render_to_response(
                    'admin/auth/sms_result.html',
                    {
                        'redirect': request.get_full_path(),
                        'success_num': successful,
                        'fail': fail
                    },
                )

        if not form:
            form = SendWelcomeSmsForm(
                initial={
                    '_selected_action': request.POST.getlist(
                        admin.ACTION_CHECKBOX_NAME,
                    ),
                }
            )
        return render_to_response(
            'admin/auth/send_sms.html',
            {
                'sms_form': form,
                'learners': queryset
            },
            context_instance=template.RequestContext(request)
        )
    send_sms.short_description = "Send sms to learners"
    actions = ['send_sms']

    def completed_questions(self, learner):
        return ParticipantQuestionAnswer.objects.filter(
            participant__learner=learner
        ).count()
    completed_questions.short_description = "Completed Questions"
    completed_questions.allow_tags = True

    def percentage_correct(self, learner):
        complete = self.completed_questions(learner)
        if complete > 0:
            return ParticipantQuestionAnswer.objects.filter(
                participant__learner=learner,
                correct=True
            ).count() * 100 / complete
        else:
            return 0
    percentage_correct.short_description = "Percentage correct"
    percentage_correct.allow_tags = True

# Auth
admin.site.register(SystemAdministrator, SystemAdministratorAdmin)
admin.site.register(SchoolManager, SchoolManagerAdmin)
admin.site.register(CourseManager, CourseManagerAdmin)
admin.site.register(CourseMentor, CourseMentorAdmin)
admin.site.register(Learner, LearnerAdmin)
