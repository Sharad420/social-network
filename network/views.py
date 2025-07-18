import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


from .models import User, Post, Follow, Comment


# This is shown regardless of login or not, only the ability to create a new post is restricted.
def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

# Change in prod, always use a csrf_token
def newpost(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content").strip()
        # Validate the content of the post and handle it gracefully.
        if not content:
            return JsonResponse(data={"error": "Content cannot be empty."}, status=400)

        # Save the new post into the database.
        post = Post(user=request.user, content=content)
        post.save()
        return JsonResponse(data={"message": f"New post created with content: {content}"}, status=200)
    return JsonResponse(data={"error":"Method not allowed"}, status=405)

def _get_user_posts(user):
    return Post.objects.filter(user=user).order_by("-timestamp")

def posts(request, type):
    if request.method == "GET":
        page_number = request.GET.get("page", 1)
        # Fetch posts based on the type parameter.
        if type == "all":
            posts = Post.objects.all().order_by("-timestamp")
        elif type == "following":
            following_users = Follow.objects.filter(followers=request.user).values_list("following", flat=True)
            posts = Post.objects.filter(user__in=following_users).order_by("-timestamp")
        elif type == "user": 
            # ACTUALLY NEVER HITTING THIS ROUTE THO, MAYBE IN THE FUTURE.
            username = request.GET.get("username")
            if not username:
                return JsonResponse({"error": "Username not provided"}, status=400)
            try:
                user = User.objects.get(username=username)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)

            posts = Post.objects.filter(user=user).order_by("-timestamp")
            paginator = Paginator(posts, 10)
            page = paginator.get_page(page_number)
            serialized_posts = [post.serialize(request_user=request.user) for post in page.object_list]

            return JsonResponse({
                "posts": serialized_posts,
                "has_next": page.has_next(),
                "has_previous": page.has_previous(),
                "current_page": page.number,
                "num_pages": paginator.num_pages,
            }, safe=False)
        else:
            return JsonResponse(data={"error": "Invalid type parameter."}, status=400)
        
        paginator = Paginator(posts, 10)
        page = paginator.get_page(page_number)
        # Serialize the posts into a JSON response.
        serialized_posts = [post.serialize(request_user=request.user) for post in page.object_list]
        return JsonResponse({
            "posts": serialized_posts,
            "has_next": page.has_next(),
            "has_previous": page.has_previous(),
            "current_page": page.number,
            "num_pages": paginator.num_pages,
        }, safe=False)
    return JsonResponse(data={"error": "Method not allowed"}, status=405)


@login_required
def profile(request, username):
    if request.user.is_authenticated is False:
        return HttpResponseRedirect(reverse("index"))
    
    data = _get_user_info(request, username)
    if data is None:
        return HttpResponseNotFound("User not found.")
    return render(request, "network/profile.html", {
        # Sending context as JSON.
        "profile_data": json.dumps(data)
    })


def _get_user_info(request, username):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return None
    
    # Get the following and followers count
    followers_count=Follow.objects.filter(following=user).count()
    following_count=Follow.objects.filter(followers=user).count()

    # Get the posts of the user
    posts = _get_user_posts(user)
    serialized_posts = [post.serialize(request_user=request.user) for post in posts]

    # Get if the current user is following the requested user. O(1) operation. Can think of caching later on.
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(followers=request.user, following=user).exists()

    # Build the API response
    return {
        "username": user.username,
        "name": f"{user.first_name} {user.last_name}",
        "followers":followers_count,
        "following":following_count,
        "is_following":is_following,
        "posts":serialized_posts
    }


@login_required
def follow(request, username):
    if request.method == "POST":

        try:
            user_to_follow = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return JsonResponse(data={"error": "User not available"}, status=404)
        
        if request.user == user_to_follow:
            return JsonResponse(data={"error": "You can't follow yourself bruh"}, status=400)
            
        # Get the relation if already exists so that we can unfollow, or create it.
        follow_relation, created = Follow.objects.get_or_create(
            following=user_to_follow, followers=request.user
        )
        # If already created, we unfollow.
        if not created:
            follow_relation.delete()
            is_following = False
        else:
            is_following = True

        data = {
            "is_following":is_following,
            "followers": Follow.objects.filter(following=user_to_follow).count()
        }

        return JsonResponse(data=data, status=200)

    return JsonResponse(data={"error": "Method not allowed"}, status=405)

@login_required
def following(request):
    return render(request, "network/following.html")


@login_required
def toggle_like(request, postid):
    if request.method == "POST":
        try:
            post_to_like = Post.objects.get(id=postid)
        except ObjectDoesNotExist:
            return JsonResponse(data={"error":"Post does not exist"}, status=404)
        
        if (request.user.is_authenticated) and (request.user in post_to_like.likes.all()):
            post_to_like.likes.remove(request.user)
        else:
            post_to_like.likes.add(request.user)

        # Another parameter added to serialize method.
        post_data = post_to_like.serialize(request_user=request.user)
        return JsonResponse(data=post_data, status=200)
    return JsonResponse(data={"error":"Method not allowed"}, status=405)


@login_required
def show_likers(request, postid):
    if request.method == "GET":
        try:
            post = Post.objects.get(id=postid)
        except ObjectDoesNotExist:
            return JsonResponse(data={"error":"Post not found"}, status=404)
        
        likers = post.likes.all()
        # Only username required
        data = [{"username":user.username} for user in likers]
        return JsonResponse(data=data, safe=False, status=200)
    return JsonResponse(data={"error":"Method not allowed"}, status=405)

@login_required
def show_follow_data(request, username, follow_type):
    if request.method == "GET":
        if follow_type not in ["following", "followers"]:
            return JsonResponse(data={"error": "Not a valid request"}, status=400)
        
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return JsonResponse(data={"error":"User not found"}, status=404)
        
        fol_list = []
        if follow_type == "following":
            # select_related Does a join to reduce number of queries, read up a little more about it.
            fol_list = Follow.objects.filter(followers=user).select_related("following")
            users = [f.following for f in fol_list]
        elif follow_type == "followers":
            fol_list = Follow.objects.filter(following=user).select_related("followers")
            users = [f.followers for f in fol_list]

        data = {
            "follow_type":follow_type, 
            "users":[{"username":user.username} for user in users]
        }
        return JsonResponse(data=data, safe=False, status=200)
    return JsonResponse(data={"error":"Method not alllowed"}, status=405)

def comments(request, postid):
    try:
        post = Post.objects.get(id=postid)
    except ObjectDoesNotExist:
        return JsonResponse(data={"error":"Post not found"}, status=404)
    
    if request.method == "GET":
        comments_list = post.comments.all().order_by("-timestamp")
        return JsonResponse(data=[c.serialize() for c in comments_list], safe=False, status=200)
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse(data={"error": "Authentication required to comment."}, status=403)
        data = json.loads(request.body)
        content = data.get("content").strip()
        # Validate the content of the post and handle it gracefully.
        if not content:
            return JsonResponse(data={"error": "Content cannot be empty."}, status=400)

        # Save the new post into the database.
        comment = Comment(user=request.user, content=content, post=post)
        comment.save()

        return JsonResponse(data=comment.serialize(), status=200)
    return JsonResponse(data={"error":"Method not allowed"}, status=405)


@login_required
def edit(request, postid):
    if request.method == "POST":
        try:
            post = Post.objects.get(id=postid)
        except ObjectDoesNotExist:
            return JsonResponse({"error":"Post not found"}, status=404)
        
        if request.user != post.user:
            return JsonResponse({"error":"Unauthorized"}, status=403)
        
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        if not content:
            return JsonResponse({"error":"Content cannot be empty"}, status=400)
        post.content = content
        post.save()
        return JsonResponse(post.serialize(request.user), status=200)
    return JsonResponse({"error":"Mehtod not allowed"}, status=405)


@login_required
def delete_post(request, postid):
    try:
        post = Post.objects.get(id=postid)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    if post.user != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method == "DELETE":
        post.delete()
        return JsonResponse({"message": "Post deleted"}, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)
