import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Box, Paper, Typography, Grid, Button } from '@mui/material';
import AnalysisDashboard from '../components/AnalysisDashboard';
import config from '../config';

const AnalysisPage = () => {
    const { user } = useAuth();
    const [analysisData, setAnalysisData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAnalysisData = async () => {
            try {
                const response = await fetch(
                    `${config.api.baseUrl}${config.api.endpoints.analysis.getAnalysis}/${user.id}`
                );
                const data = await response.json();
                setAnalysisData(data);
            } catch (error) {
                console.error('Error fetching analysis data:', error);
            } finally {
                setLoading(false);
            }
        };

        if (user) {
            fetchAnalysisData();
        }
    }, [user]);

    const handleExport = async () => {
        try {
            const response = await fetch(
                `${config.api.baseUrl}${config.api.endpoints.analysis.exportAnalysis}/${user.id}?format=pdf`
            );
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'analysis-report.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting analysis:', error);
        }
    };

    if (loading) {
        return <Typography>Loading...</Typography>;
    }

    return (
        <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                        <Typography variant="h4">Analysis Dashboard</Typography>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleExport}
                            disabled={!analysisData}
                        >
                            Export Report
                        </Button>
                    </Box>
                </Grid>
                <Grid item xs={12}>
                    <AnalysisDashboard userId={user.id} />
                </Grid>
                {analysisData?.latest_analysis && (
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>
                                Latest Analysis
                            </Typography>
                            <Typography variant="body1">
                                Dyslexia Probability: {(analysisData.latest_analysis.dyslexia_probability * 100).toFixed(2)}%
                            </Typography>
                            <Typography variant="body1">
                                Confidence Level: {analysisData.latest_analysis.confidence_level}
                            </Typography>
                        </Paper>
                    </Grid>
                )}
                {analysisData?.latest_analysis?.recommendations && (
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>
                                Recommendations
                            </Typography>
                            <ul>
                                {analysisData.latest_analysis.recommendations.map((rec, index) => (
                                    <li key={index}>{rec.message}</li>
                                ))}
                            </ul>
                        </Paper>
                    </Grid>
                )}
            </Grid>
        </Box>
    );
};

export default AnalysisPage; 