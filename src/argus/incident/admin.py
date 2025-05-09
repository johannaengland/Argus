from urllib.parse import urlsplit

from django.contrib import admin
from django.contrib.admin import widgets as admin_widgets
from django.contrib.auth import get_user_model
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe

from argus.util.admin_utils import add_elements_to_deleted_objects, list_filter_factory
from . import fields, widgets
from .forms import AddSourceSystemForm, FakeIncidentForm
from .models import (
    Acknowledgement,
    Event,
    Incident,
    IncidentQuerySet,
    IncidentRelation,
    IncidentRelationType,
    IncidentTagRelation,
    SourceSystem,
    SourceSystemType,
    Tag,
    create_fake_incident,
)

User = get_user_model()


class TextWidgetsOverrideModelAdmin(admin.ModelAdmin):
    text_input_form_fields = ()
    url_input_form_fields = ()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        for form_field in self.text_input_form_fields:
            form.base_fields[form_field].widget = admin_widgets.AdminTextInputWidget()
        for form_field in self.url_input_form_fields:
            form.base_fields[form_field].widget = admin_widgets.AdminURLFieldWidget()

        return form


class SourceSystemTypeAdmin(TextWidgetsOverrideModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    text_input_form_fields = ("name",)


class SourceSystemAdmin(TextWidgetsOverrideModelAdmin):
    list_display = ("name", "type", "user")
    search_fields = ("name", "user__username")
    list_filter = ("type",)

    text_input_form_fields = ("name",)
    raw_id_fields = ("user",)

    def get_form(self, request, obj=None, **kwargs):
        # If add form (instead of change form):
        if not obj:
            kwargs["form"] = AddSourceSystemForm

        return super().get_form(request, obj, **kwargs)

    def get_deleted_objects(self, objs, request):
        to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        new_to_delete = add_elements_to_deleted_objects(objs, to_delete, lambda source: [source.user], self.admin_site)
        model_count[User._meta.verbose_name_plural] = len(objs)

        return new_to_delete, model_count, perms_needed, protected


class TagAdmin(TextWidgetsOverrideModelAdmin):
    list_display = ("get_str",)
    search_fields = ("key", "value")
    ordering = [Concat("key", "value")]

    text_input_form_fields = ("key", "value")

    def get_str(self, tag: Tag):
        return tag

    get_str.short_description = "Tag"
    get_str.admin_order_field = Concat("key", "value")


class IncidentAdmin(TextWidgetsOverrideModelAdmin):
    class IncidentTagRelationInline(admin.TabularInline):
        model = IncidentTagRelation
        ordering = ["tag__key", "tag__value"]
        readonly_fields = ("added_time",)
        raw_id_fields = ("tag", "added_by")
        extra = 0

    change_list_template = "incident/admin/incident_change_list.html"

    inlines = [IncidentTagRelationInline]

    list_display = (
        "source_incident_id",
        "start_time",
        "get_end_time",
        "source",
        "get_tags",
        "description",
        "get_details_url",
        "get_ticket_url",
        "get_open",
        "get_shown",
    )
    list_display_links = (
        "source_incident_id",
        "start_time",
    )
    search_fields = (
        "description",
        "source_incident_id",
        "source__name",
        "source__type__name",
        "incident_tag_relations__tag__key",
        "incident_tag_relations__tag__value",
        "ticket_url",
        "details_url",
    )
    date_hierarchy = "start_time"
    list_filter = (
        list_filter_factory("stateful", lambda qs, yes_filter: qs.stateful() if yes_filter else qs.stateless()),
        list_filter_factory("open", lambda qs, yes_filter: qs.open() if yes_filter else qs.closed()),
        list_filter_factory("acked", lambda qs, yes_filter: qs.acked() if yes_filter else qs.not_acked()),
        "level",
        list_filter_factory("has ticket", lambda qs, yes_filter: qs.has_ticket() if yes_filter else qs.lacks_ticket()),
        list_filter_factory(
            "has details url", lambda qs, yes_filter: qs.has_details_url() if yes_filter else qs.lacks_details_url()
        ),
        "source__type",
        "source",
    )
    exclude = ("search_text",)

    text_input_form_fields = ("source_incident_id",)
    url_input_form_fields = ("details_url", "ticket_url")

    def get_end_time(self, incident: Incident):
        return incident.end_time_str

    get_end_time.short_description = "End time"
    get_end_time.admin_order_field = "end_time"

    def get_tags(self, incident: Incident):
        html_open_tag = '<div style="display: inline-block; white-space: nowrap;">'
        html_bullet = "<b>&bull;</b>"
        return format_html_join(
            mark_safe("<br />"),
            f"{html_open_tag}{html_bullet} {{}}</div>",
            ((tag,) for tag in incident.deprecated_tags),
        )

    get_tags.short_description = "Tags"

    def get_details_url(self, incident: Incident):
        url = incident.pp_details_url()
        if not url:
            return ""
        scheme, netloc, *_ = urlsplit(url)
        if scheme and netloc:  # absolute url: linkify!
            return format_html('<a href="{}" title="{}">Link</a>', url, url)
        return url  # relative url

    get_details_url.short_description = "Details url"

    def get_ticket_url(self, incident: Incident):
        url = incident.ticket_url.strip()
        if url:
            return format_html('<a href="{}" title="{}">Link</a>', url, url)
        return ""

    get_ticket_url.short_description = "Ticket url"

    def get_open(self, incident: Incident):
        return incident.open

    get_open.short_description = "Open"
    get_open.boolean = True

    def get_shown(self, incident: Incident):
        return incident.open and not incident.acked

    get_shown.short_description = "Shown"
    get_shown.boolean = True

    def get_urls(self):
        orig_urls = super().get_urls()
        urls = [path("fake/", self.admin_site.admin_view(self.add_fake_incident), name="add-fake-incident")]
        return urls + orig_urls

    def add_fake_incident(self, request):
        request.current_app = self.admin_site.name
        if request.method == "POST":
            form = FakeIncidentForm(request.POST)
            if form.is_valid():
                tags = form.cleaned_data.get("tags", None)
                description = form.cleaned_data.get("description", None)
                stateful = form.cleaned_data.get("stateful")
                level = form.cleaned_data.get("level", None)
                metadata = form.cleaned_data.get("metadata", None)
                create_fake_incident(
                    tags=tags,
                    description=description,
                    stateful=stateful,
                    level=level,
                    metadata=metadata,
                )
                return HttpResponseRedirect("../")
        else:
            form = FakeIncidentForm()

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})
        context = {
            "title": "Add fake incident",
            "subtitle": None,
            "adminform": admin_form,
            "opts": self.model._meta,
            "errors": None,
            **self.admin_site.each_context(request),
        }
        return TemplateResponse(request, "incident/admin/fake_incident_add_form.html", context)

    def get_form(self, request, obj: Incident = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        end_time_field = form.base_fields["end_time"]
        end_time_field_inheritance_attrs = {
            attr: getattr(end_time_field, attr) for attr in ("required", "label", "help_text")
        }
        end_time = obj.end_time if obj else None
        form.base_fields["end_time"] = fields.SplitDateTimeInfinityField(
            **end_time_field_inheritance_attrs, widget=widgets.AdminSplitDateTimeInfinity(initial_value=end_time)
        )
        return form

    def get_queryset(self, request):
        qs: IncidentQuerySet = super().get_queryset(request)
        # Reduce number of database calls
        return qs.prefetch_default_related().prefetch_related("events__ack")


class IncidentRelationTypeAdmin(TextWidgetsOverrideModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    text_input_form_fields = ("name",)


class IncidentRelationAdmin(admin.ModelAdmin):
    list_display = ("get_str", "type", "description")
    search_fields = ("incident1__source_incident_id", "incident2__source_incident_id")
    list_filter = ("type",)
    list_select_related = ("incident1", "incident2", "type")

    raw_id_fields = ("incident1", "incident2")

    def get_str(self, incident_relation: IncidentRelation):
        return incident_relation

    get_str.short_description = "Incident relation"


class EventAdmin(admin.ModelAdmin):
    list_display = ("get_id", "timestamp", "type", "actor", "description")
    search_fields = (
        "incident__pk",
        "incident__source_incident_id",
        "incident__description",
        "actor__username",
        "actor__first_name",
        "actor__last_name",
        "description",
    )
    list_filter = ("type", "incident__source", "incident__source__type")

    raw_id_fields = ("incident", "actor")

    def get_id(self, event: Event):
        source_incident_str = f"{event.incident.source_incident_id} in {event.incident.source}"
        return mark_safe(f"#{event.incident.pk} &emsp; [{source_incident_str}]")

    get_id.short_description = "Incident ID"
    get_id.admin_order_field = "incident__pk"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Reduce number of database calls
        return qs.select_related("actor").prefetch_related("incident__source__type")


class AcknowledgementAdmin(admin.ModelAdmin):
    list_display = ("get_id", "get_timestamp", "expiration", "get_actor", "get_description")
    search_fields = (
        "event__incident__pk",
        "event__incident__source_incident_id",
        "event__incident__description",
        "event__actor__username",
        "event__actor__first_name",
        "event__actor__last_name",
        "event__description",
    )
    list_filter = ("event__incident__source", "event__incident__source__type")

    raw_id_fields = ("event",)

    def get_readonly_fields(self, request, obj=None):
        # Prevent `event` from being changed, as it contains the acknowledgement's data
        return ("event",) if obj else ()

    def get_id(self, ack: Acknowledgement):
        source_incident_str = f"{ack.event.incident.source_incident_id} in {ack.event.incident.source}"
        return mark_safe(f"#{ack.event.incident.pk} &emsp; [{source_incident_str}]")

    get_id.short_description = "Incident ID"
    get_id.admin_order_field = "event__incident__pk"

    def get_timestamp(self, ack: Acknowledgement):
        return ack.event.timestamp

    get_timestamp.short_description = "Timestamp"
    get_timestamp.admin_order_field = "event__timestamp"

    def get_actor(self, ack: Acknowledgement):
        return ack.event.actor

    get_actor.short_description = "Actor"
    get_actor.admin_order_field = "event__actor"

    def get_description(self, ack: Acknowledgement):
        return ack.event.description

    get_description.short_description = "Description"
    get_description.admin_order_field = "event__description"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Reduce number of database calls
        return qs.prefetch_related("event__incident__source__type", "event__actor")

    def get_deleted_objects(self, objs, request):
        to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        new_to_delete = add_elements_to_deleted_objects(objs, to_delete, lambda ack: [ack.event], self.admin_site)
        model_count[Event._meta.verbose_name_plural] = len(objs)

        return new_to_delete, model_count, perms_needed, protected


admin.site.register(SourceSystemType, SourceSystemTypeAdmin)
admin.site.register(SourceSystem, SourceSystemAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(IncidentRelation, IncidentRelationAdmin)
admin.site.register(IncidentRelationType, IncidentRelationTypeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Acknowledgement, AcknowledgementAdmin)
