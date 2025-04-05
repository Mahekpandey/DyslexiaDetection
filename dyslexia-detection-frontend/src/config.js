const config = {
    api: {
        baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
        endpoints: {
            auth: {
                login: '/auth/login',
                register: '/auth/register',
                verify: '/auth/verify',
            },
            analysis: {
                getAnalysis: '/analysis/user',
                exportAnalysis: '/analysis/export',
                generateSample: '/test/sample-data',
            },
        },
    },
    features: {
        enableRealTimeUpdates: true,
        enableExport: true,
    },
    ui: {
        maxChartPoints: 50,
        refreshInterval: 30000, // 30 seconds
    },
};

export default config; 