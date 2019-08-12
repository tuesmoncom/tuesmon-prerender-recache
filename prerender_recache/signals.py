from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from tuesmon.projects.models import Project
from tuesmon.projects.milestones.models import Milestone
from tuesmon.projects.userstories.models import UserStory
from tuesmon.projects.tasks.models import Task
from tuesmon.projects.issues.models import Issue
from tuesmon.projects.wiki.models import WikiPage
from tuesmon.projects.epics.models import Epic
from tuesmon.users.models import User
from tuesmon.front.urls import urls
from .service import recache_schedule

def build_url(name, *params):
    return "{}://{}{}".format(
        settings.SITES['front']['scheme'],
        settings.SITES['front']['domain'],
        urls[name].format(*params)
    )


def recache_user_profile(user):
    url = build_url("user", user.username)
    recache_schedule(url)


def recache_project_profile(project):
    url = build_url("project", project.slug)
    recache_schedule(url)


def recache_wiki_page(wiki_page):
    url = build_url("wiki", wiki_page.project.slug, wiki_page.slug)
    recache_schedule(url)


def recache_issue(issue):
    url = build_url("issue", issue.project.slug, issue.ref)
    recache_schedule(url)


def recache_task(task):
    url = build_url("task", task.project.slug, task.ref)
    recache_schedule(url)


def recache_epic(epic):
    url = build_url("epic", epic.project.slug, epic.ref)
    recache_schedule(url)


def recache_us(us):
    url = build_url("userstory", us.project.slug, us.ref)
    recache_schedule(url)


def recache_taskboard(milestone):
    url = build_url("taskboard", milestone.project.slug, milestone.slug)
    recache_schedule(url)


def recache_backlog(project):
    url = build_url("backlog", project.slug)
    recache_schedule(url)


def recache_kanban(project):
    url = build_url("kanban", project.slug)
    recache_schedule(url)


@receiver(post_save, sender=User)
def user_post_save(update_fields, instance, **kwargs):
    # No recache on last_login update
    if update_fields and len(update_fields) == 1 and 'last_login' in update_fields:
        return

    recache_user_profile(instance)


@receiver(post_save, sender=WikiPage)
def wiki_page_post_save(instance, **kwargs):
    recache_project_profile(instance.project)
    recache_wiki_page(instance)


@receiver(post_save, sender=Issue)
def issue_post_save(instance, **kwargs):
    recache_project_profile(instance.project)
    recache_issue(instance)


@receiver(post_save, sender=Task)
def task_post_save(instance, **kwargs):
    recache_project_profile(instance.project)
    recache_task(instance)
    if instance.user_story:
        recache_us(instance.user_story)
    if instance.milestone:
        recache_taskboard(instance.milestone)
    recache_backlog(instance.project)
    recache_kanban(instance.project)


@receiver(post_save, sender=Epic)
def epic_post_save(instance, **kwargs):
    recache_project_profile(instance.project)
    recache_epic(instance)
    for us in instance.user_stories.all():
        recache_us(us)
    recache_backlog(instance.project)
    recache_kanban(instance.project)


@receiver(post_save, sender=UserStory)
def us_post_save(instance, **kwargs):
    recache_project_profile(instance.project)
    recache_us(instance)
    for task in instance.tasks.all():
        recache_task(task)
    if instance.milestone:
        recache_taskboard(instance.milestone)
    recache_backlog(instance.project)
    recache_kanban(instance.project)

@receiver(post_save, sender=Milestone)
def milestone_post_save(instance, **kwargs):
    recache_project_profile(instance.project)
    recache_taskboard(instance)
    for task in instance.tasks.all():
        recache_task(task)
    for us in instance.user_stories.all():
        recache_us(us)
    recache_backlog(instance.project)
    recache_kanban(instance.project)

@receiver(post_save, sender=Project)
def project_post_save(instance, **kwargs):
    recache_project_profile(instance)
    recache_backlog(instance)
    recache_kanban(instance)
