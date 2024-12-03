import { Box, Typography, Container } from '@mui/material'

const Footer = () => {
  return (
    <Box component="footer" sx={{ py: 3, borderTop: '1px solid #E0E0E0' }}>
      <Container maxWidth={false}>
        <Typography variant="body2" color="text.secondary" align="center">
          © 2024 Blog. All rights reserved.
        </Typography>
      </Container>
    </Box>
  )
}

export default Footer 