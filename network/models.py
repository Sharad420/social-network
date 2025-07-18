from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # One post can be liked by many users, and one user can like many posts.
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    # Counts can be accessed directly with posts.likes.count()

    def serialize(self, request_user=None):
        return {
            "id": self.id,
            "user":self.user.username,
            "content":self.content,
            "timestamp":self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
            "likes": self.likes.count(),
            "liked": request_user in self.likes.all() if request_user and request_user.is_authenticated else False,
            "comments": self.comments.count()
        }

# Understand this relationship, recommended to use this over ManytoMany in User class to avoid complications.
class Follow(models.Model):
    # Alice follows Bob and following set gives all FOLLOW objects where the follower is Alice.
    followers = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    # Bob is followed by Alice and follower_set gives all FOLLOW objects where the following is Bob.
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')

    class Meta:
        unique_together=("followers","following")

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "user":self.user.username,
            "content":self.content,
            "timestamp":self.timestamp.strftime("%d-%m-%Y %H:%M:%S")
        }
