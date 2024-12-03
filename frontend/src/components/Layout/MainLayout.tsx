import { Box, Container, styled } from '@mui/material';
import Header from './Header';
import Footer from './Footer';

const MainContainer = styled(Container)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(2),
  [theme.breakpoints.up('sm')]: {
    padding: theme.spacing(4),
  },
}));

const ContentWrapper = styled(Box)(({ theme }) => ({
  flex: 1,
  marginTop: theme.spacing(8),
  marginBottom: theme.spacing(8),
}));

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <MainContainer maxWidth={false}>
      <Header />
      <ContentWrapper>{children}</ContentWrapper>
      <Footer />
    </MainContainer>
  );
};

export default MainLayout; 