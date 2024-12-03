from core.base_service import BaseService
from posts.models import Post


class PostService(BaseService[Post]):
    model = Post

    def get_user_posts(self, user_id: int) -> list[Post]:
        return self.filter(author_id=user_id) 