import React from 'react';
import { Box, AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Layout = ({ children }) => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Dyslexia Detection
                    </Typography>
                    {user ? (
                        <>
                            <Button color="inherit" onClick={() => navigate('/dashboard')}>
                                Dashboard
                            </Button>
                            <Button color="inherit" onClick={() => navigate('/analysis')}>
                                Analysis
                            </Button>
                            <Button color="inherit" onClick={handleLogout}>
                                Logout
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button color="inherit" onClick={() => navigate('/login')}>
                                Login
                            </Button>
                            <Button color="inherit" onClick={() => navigate('/register')}>
                                Register
                            </Button>
                        </>
                    )}
                </Toolbar>
            </AppBar>
            <Container component="main" sx={{ flex: 1, py: 4 }}>
                {children}
            </Container>
            <Box component="footer" sx={{ py: 3, bgcolor: 'background.paper' }}>
                <Container maxWidth="lg">
                    <Typography variant="body2" color="text.secondary" align="center">
                        © {new Date().getFullYear()} Dyslexia Detection System
                    </Typography>
                </Container>
            </Box>
        </Box>
    );
};

export default Layout; 