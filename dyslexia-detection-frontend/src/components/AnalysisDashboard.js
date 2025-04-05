import React, { useState, useEffect } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import { Box, Paper, Typography, Grid } from '@mui/material';
import config from '../config';

const AnalysisDashboard = ({ userId }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(
                    `${config.api.baseUrl}${config.api.endpoints.analysis.getAnalysis}/${userId}`
                );
                const result = await response.json();
                
                if (result.assessments) {
                    const chartData = result.assessments.map(assessment => ({
                        date: new Date(assessment.timestamp).toLocaleDateString(),
                        reading: assessment.reading_score,
                        spelling: assessment.spelling_score,
                        responseTime: assessment.response_time_score,
                    }));
                    setData(chartData.slice(-config.ui.maxChartPoints));
                }
            } catch (error) {
                console.error('Error fetching analysis data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, config.ui.refreshInterval);
        return () => clearInterval(interval);
    }, [userId]);

    if (loading) {
        return <Typography>Loading...</Typography>;
    }

    return (
        <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Assessment Progress
                        </Typography>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="reading"
                                    stroke="#8884d8"
                                    name="Reading Score"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="spelling"
                                    stroke="#82ca9d"
                                    name="Spelling Score"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="responseTime"
                                    stroke="#ffc658"
                                    name="Response Time Score"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default AnalysisDashboard; 