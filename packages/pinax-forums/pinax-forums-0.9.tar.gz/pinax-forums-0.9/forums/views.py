from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from django.contrib import messages

from account.decorators import login_required

from forums.forms import ThreadForm, ReplyForm
from forums.models import (
    Forum,
    ForumCategory,
    ForumReply,
    ForumThread,
    ThreadSubscription,
    UserPostCount
)


def forums(request):

    categories = ForumCategory.objects.filter(parent__isnull=True)
    categories = categories.order_by("title")

    most_active_forums = Forum.objects.order_by("-post_count")[:5]
    most_viewed_forums = Forum.objects.order_by("-view_count")[:5]
    most_active_members = UserPostCount.objects.order_by("-count")[:5]

    latest_posts = ForumReply.objects.order_by("-created")[:10]
    latest_threads = ForumThread.objects.order_by("-last_modified")
    most_active_threads = ForumThread.objects.order_by("-reply_count")
    most_viewed_threads = ForumThread.objects.order_by("-view_count")

    return render_to_response("forums/forums.html", {
        "categories": categories,
        "most_active_forums": most_active_forums,
        "most_viewed_forums": most_viewed_forums,
        "most_active_members": most_active_members,
        "latest_posts": latest_posts,
        "latest_threads": latest_threads,
        "most_active_threads": most_active_threads,
        "most_viewed_threads": most_viewed_threads,
    }, context_instance=RequestContext(request))


def forum_category(request, category_id):

    category = get_object_or_404(ForumCategory, id=category_id)
    forums = category.forums.order_by("title")

    return render_to_response("forums/category.html", {
        "category": category,
        "forums": forums,
    }, context_instance=RequestContext(request))


def forum(request, forum_id):

    forum = get_object_or_404(Forum, id=forum_id)
    threads = forum.threads.order_by("-sticky", "-last_modified")

    can_create_thread = all([
        request.user.has_perm("forums.add_forumthread", obj=forum),
        not forum.closed,
    ])

    return render_to_response("forums/forum.html", {
        "forum": forum,
        "threads": threads,
        "can_create_thread": can_create_thread,
    }, context_instance=RequestContext(request))


def forum_thread(request, thread_id):
    qs = ForumThread.objects.select_related("forum")
    thread = get_object_or_404(qs, id=thread_id)

    can_create_reply = all([
        request.user.has_perm("forums.add_forumreply", obj=thread),
        not thread.closed,
        not thread.forum.closed,
    ])

    if can_create_reply:
        if request.method == "POST":
            reply_form = ReplyForm(request.POST)

            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.thread = thread
                reply.author = request.user
                reply.save()

                # subscribe the poster to the thread if requested (default value is True)
                if reply_form.cleaned_data["subscribe"]:
                    thread.subscribe(reply.author, "email")

                # all users are automatically subscribed to onsite
                thread.subscribe(reply.author, "onsite")

                return HttpResponseRedirect(reverse("forums_thread", args=[thread.id]))
        else:
            reply_form = ReplyForm()
    else:
        reply_form = None

    order_type = request.GET.get("order_type", "asc")
    posts = ForumThread.objects.posts(thread, reverse=(order_type == "desc"))
    thread.inc_views()

    return render_to_response("forums/thread.html", {
        "thread": thread,
        "posts": posts,
        "order_type": order_type,
        "subscribed": thread.subscribed(request.user, "email"),
        "reply_form": reply_form,
        "can_create_reply": can_create_reply,
    }, context_instance=RequestContext(request))


@login_required
def post_create(request, forum_id):

    member = request.user.get_profile()
    forum = get_object_or_404(Forum, id=forum_id)

    if forum.closed:
        messages.error(request, "This forum is closed.")
        return HttpResponseRedirect(reverse("forums_forum", args=[forum.id]))

    can_create_thread = request.user.has_perm("forums.add_forumthread", obj=forum)

    if not can_create_thread:
        messages.error(request, "You do not have permission to create a thread.")
        return HttpResponseRedirect(reverse("forums_forum", args=[forum.id]))

    if request.method == "POST":
        form = ThreadForm(request.POST)

        if form.is_valid():
            thread = form.save(commit=False)
            thread.forum = forum
            thread.author = request.user
            thread.save()

            # subscribe the poster to the thread if requested (default value is True)
            if form.cleaned_data["subscribe"]:
                thread.subscribe(thread.author, "email")

            # all users are automatically subscribed to onsite
            thread.subscribe(thread.author, "onsite")

            return HttpResponseRedirect(reverse("forums_thread", args=[thread.id]))
    else:
        form = ThreadForm()

    return render_to_response("forums/post_create.html", {
        "form": form,
        "member": member,
        "forum": forum
    }, context_instance=RequestContext(request))


@login_required
def reply_create(request, thread_id):

    member = request.user.get_profile()
    thread = get_object_or_404(ForumThread, id=thread_id)

    if thread.closed:
        messages.error(request, "This thread is closed.")
        return HttpResponseRedirect(reverse("forums_thread", args=[thread.id]))

    can_create_reply = request.user.has_perm("forums.add_forumreply", obj=thread)

    if not can_create_reply:
        messages.error(request, "You do not have permission to reply to this thread.")
        return HttpResponseRedirect(reverse("forums_thread", args=[thread.id]))

    if request.method == "POST":
        form = ReplyForm(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.thread = thread
            reply.author = request.user
            reply.save()

            # subscribe the poster to the thread if requested (default value is True)
            if form.cleaned_data["subscribe"]:
                thread.subscribe(reply.author, "email")

            # all users are automatically subscribed to onsite
            thread.subscribe(reply.author, "onsite")

            return HttpResponseRedirect(reverse("forums_thread", args=[thread_id]))
    else:
        quote = request.GET.get("quote")  # thread id to quote
        initial = {}

        if quote:
            quote_reply = ForumReply.objects.get(id=int(quote))
            initial["content"] = "\"%s\"" % quote_reply.content

        form = ReplyForm(initial=initial)

    first_reply = not ForumReply.objects.filter(thread=thread, author=request.user).exists()

    return render_to_response("forums/reply_create.html", {
        "form": form,
        "member": member,
        "thread": thread,
        "subscribed": thread.subscribed(request.user, "email"),
        "first_reply": first_reply,
    }, context_instance=RequestContext(request))


@login_required
def post_edit(request, post_kind, post_id):

    if post_kind == "thread":
        post = get_object_or_404(ForumThread, id=post_id)
        thread_id = post.id
        form_class = ThreadForm
    elif post_kind == "reply":
        post = get_object_or_404(ForumReply, id=post_id)
        thread_id = post.thread.id
        form_class = ReplyForm
    else:
        raise Http404()

    if not post.editable(request.user):
        raise Http404()

    if request.method == "POST":
        form = form_class(request.POST, instance=post, no_subscribe=True)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("forums_thread", args=[thread_id]))
    else:
        form = form_class(instance=post, no_subscribe=True)

    return render_to_response("forums/post_edit.html", {
        "post": post,
        "form": form,
    }, context_instance=RequestContext(request))


@login_required
def subscribe(request, thread_id):
    user = request.user
    thread = get_object_or_404(ForumThread, pk=thread_id)

    if request.method == "POST":
        thread.subscribe(user, "email")
        return HttpResponseRedirect(reverse("forums_thread", args=[thread_id]))
    else:
        ctx = RequestContext(request, {"thread": thread})
        return render_to_response("forums/subscribe.html", ctx)


@login_required
def unsubscribe(request, thread_id):
    user = request.user
    thread = get_object_or_404(ForumThread, pk=thread_id)

    if request.method == "POST":
        thread.unsubscribe(user, "email")
        return HttpResponseRedirect(reverse("forums_thread", args=[thread_id]))
    else:
        ctx = RequestContext(request, {"thread": thread})
        return render_to_response("forums/unsubscribe.html", ctx)


@login_required
def thread_updates(request):
    subscriptions = ThreadSubscription.objects.filter(user=request.user, kind="onsite")
    subscriptions = subscriptions.select_related("thread", "user")
    subscriptions = subscriptions.order_by("-thread__last_modified")

    if request.method == "POST":
        subscriptions.filter(pk=request.POST["thread_id"]).delete()

    ctx = {
        "subscriptions": subscriptions,
    }
    ctx = RequestContext(request, ctx)
    return render_to_response("forums/thread_updates.html", ctx)
