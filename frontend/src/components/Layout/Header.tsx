import { AppBar, Box, Button, styled, Typography } from '@mui/material';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: 'transparent',
  boxShadow: 'none',
  borderBottom: '1px solid #E0E0E0',
  position: 'relative',
}));

const NavButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: '0.9rem',
  fontWeight: 500,
  '&.active': {
    color: theme.palette.text.primary,
    fontWeight: 600,
  },
  '&:hover': {
    backgroundColor: 'transparent',
    color: theme.palette.text.primary,
  },
}));

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  
  const handleAuthClick = () => {
    if (isAuthenticated) {
      logout();
    } else {
      navigate('/login');
    }
  };
  
  return (
    <StyledAppBar>
      <Box display="flex" justifyContent="space-between" alignItems="center" py={2}>
        <Typography 
          variant="h1" 
          component={Link} 
          to="/" 
          sx={{ 
            textDecoration: 'none', 
            color: 'text.primary',
            fontSize: '1.5rem',
            fontWeight: 500,
          }}
        >
          BLOG
        </Typography>
        <Box component="nav" display="flex" alignItems="center">
          <NavButton 
            component={Link} 
            to="/tech"
            className={location.pathname === '/tech' ? 'active' : ''}
          >
            TECH
          </NavButton>
          <NavButton 
            component={Link} 
            to="/guestbook"
            className={location.pathname === '/guestbook' ? 'active' : ''}
          >
            GUESTBOOK
          </NavButton>
          <Box display="flex" alignItems="center" ml={2}>
            {isAuthenticated && user && (
              <Typography 
                variant="body2" 
                sx={{ 
                  mr: 2,
                  color: 'text.secondary',
                  fontWeight: 500 
                }}
              >
                {user.username}
              </Typography>
            )}
            <NavButton onClick={handleAuthClick}>
              {isAuthenticated ? 'LOGOUT' : 'LOGIN'}
            </NavButton>
          </Box>
        </Box>
      </Box>
    </StyledAppBar>
  );
};

export default Header; 