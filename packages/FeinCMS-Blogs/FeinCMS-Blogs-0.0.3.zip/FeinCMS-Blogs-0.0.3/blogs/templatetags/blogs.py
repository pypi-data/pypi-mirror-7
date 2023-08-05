# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import datetime

from django import template
from django.db.models import F
from django.utils.dateformat import format

register = template.Library()


@register.assignment_tag
def blog_years(blog):
    if not blog:
        return

    qs = blog.posts.dates('date', 'year')
    return [dt.year for dt in qs]


@register.assignment_tag
def blog_months(blog, date=None, year=None):
    if not blog:
        return

    if date:
        year = date.year
    elif not year:
        return

    qs = blog.posts.filter(
        date__year=year,
    ).dates('date', 'month')
    return [dt.month for dt in qs]


@register.assignment_tag
def blog_days(blog, date=None, year=None, month=None):
    if not blog:
        return

    if date:
        year = date.year
        month = date.month
    elif not year or not month:
        return

    qs = blog.posts.filter(
        date__year=year,
        date__month=month,
    ).dates('date', 'day')
    return [dt.day for dt in qs]

@register.assignment_tag(takes_context=True)
def blogs_current_blog(context):
    try:
        return context['request']._blogs_current_blog
    except AttributeError:
        pass

@register.assignment_tag(takes_context=True)
def blogs_current_date(context):
    try:
        return context['request']._blogs_current_date
    except AttributeError:
        pass

@register.assignment_tag(takes_context=True)
def blogs_current_year(context):
    try:
        return context['request']._blogs_current_year
    except AttributeError:
        pass

@register.assignment_tag(takes_context=True)
def blogs_current_month(context):
    try:
        return context['request']._blogs_current_month
    except AttributeError:
        pass

@register.assignment_tag(takes_context=True)
def blogs_current_day(context):
    try:
        return context['request']._blogs_current_day
    except AttributeError:
        pass

@register.filter()
def month_name(month_number):
    date = datetime.date(year=2000, month=int(month_number), day=1)
    return format(date, "F")
