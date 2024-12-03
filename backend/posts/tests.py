from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User
from posts.models import Post, Comment, Like


class PostTests(TestCase):
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = APIClient()
        
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 다른 사용자 생성 (좋아요 테스트용)
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # 테스트 게시글 생성
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user
        )

    def test_create_post(self):
        """게시글 생성 테스트"""
        url = reverse('post-list')
        data = {
            'title': 'New Post',
            'content': '# Markdown Content\n\nTest content'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.latest('id').title, 'New Post')

    def test_create_comment(self):
        """댓글 생성 테스트"""
        url = reverse('comment-list', kwargs={'post_id': self.post.id})
        data = {'content': 'Test Comment'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_reply(self):
        """대댓글 생성 테스트"""
        # 먼저 부모 댓글 생성
        parent_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Parent Comment'
        )
        
        url = reverse('comment-list', kwargs={'post_id': self.post.id})
        data = {
            'content': 'Reply Comment',
            'parent_id': parent_comment.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_toggle_like(self):
        """좋아요 토글 테스트"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('post-like', kwargs={'pk': self.post.id})
        
        # 좋아요 생성
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 1)
        self.assertTrue(response.data['liked'])
        
        # 좋아요 취소
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)
        self.assertFalse(response.data['liked'])

    def test_like_own_post(self):
        """자신의 게시글 좋아요 시도 테스트"""
        url = reverse('post-like', kwargs={'pk': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
