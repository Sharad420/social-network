
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newpost, name="newpost"),
    path("posts/<str:type>", views.posts, name="posts"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/<str:username>/follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("posts/<int:postid>/like", views.toggle_like, name="like"), 
    path("posts/<int:postid>/likers", views.show_likers, name="show_likers"),
    path("<str:username>/<str:follow_type>", views.show_follow_data, name="show_follow_data"),
    path("posts/<int:postid>/comments", views.comments, name="comments"),
    path("posts/<int:postid>/edit", views.edit, name="edit"),
    path("posts/<int:postid>/delete", views.delete_post, name="delete")
]
