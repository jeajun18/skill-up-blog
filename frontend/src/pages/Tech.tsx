import { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';
import axios from '../utils/axios';

interface Post {
  id: number;
  title: string;
  content: string;
  author: {
    username: string;
  };
  created_at: string;
}

const Tech = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await axios.get('/posts/tech/');
        setPosts(response.data);
      } catch (err) {
        setError('포스트를 불러오는데 실패했습니다.');
        console.error('Failed to fetch posts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) return <Typography>Loading...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h1" sx={{ mb: 4 }}>
        Tech Blog
      </Typography>
      <Grid container spacing={3}>
        {posts.map((post) => (
          <Grid item xs={12} key={post.id}>
            <Card>
              <CardContent>
                <Typography variant="h2" sx={{ mb: 2 }}>
                  {post.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  작성자: {post.author.username} | 
                  작성일: {new Date(post.created_at).toLocaleDateString()}
                </Typography>
                <Typography variant="body1">
                  {post.content.slice(0, 200)}
                  {post.content.length > 200 ? '...' : ''}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Tech; 