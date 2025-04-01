class EyeTrackingClient {
    constructor() {
        this.videoElement = document.getElementById('videoElement');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.ws = null;
        this.sessionId = null;
        this.stream = null;
        this.isTracking = false;
        this.frameInterval = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isReconnecting = false;
        
        // Bind event handlers
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
        
        // Handle page unload
        window.addEventListener('beforeunload', () => {
            this.stopSession(true);
        });
    }

    updateConnectionStatus(status, isError = false) {
        if (this.connectionStatus) {
            this.connectionStatus.textContent = `Status: ${status}`;
            this.connectionStatus.className = `status${isError ? ' error' : ''}`;
        }
    }

    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden, cleanup resources
            this.stopSession(true);
        }
    }

    async startSession() {
        try {
            // Prevent multiple sessions
            if (this.ws || this.sessionId) {
                console.log('Session already active');
                return;
            }

            this.updateConnectionStatus('Requesting camera access...');

            // Get camera permission and start video
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: 640,
                    height: 480,
                    frameRate: { ideal: 30 }
                } 
            });
            this.videoElement.srcObject = this.stream;
            await this.videoElement.play();

            this.updateConnectionStatus('Starting session...');

            // Start session with backend first
            const response = await fetch('/api/start-session', {
                method: 'POST'
            });
            const data = await response.json();
            this.sessionId = data.session_id;
            console.log('Session started:', this.sessionId);

            // Then connect to WebSocket
            await this.connectWebSocket();
            
        } catch (error) {
            console.error('Error starting session:', error);
            this.updateConnectionStatus('Failed to start session: ' + error.message, true);
            this.stopSession(true);
        }
    }

    async connectWebSocket() {
        if (this.isReconnecting) {
            console.log('Already attempting to reconnect');
            return;
        }

        return new Promise((resolve, reject) => {
            try {
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    console.log('WebSocket already connected');
                    resolve();
                    return;
                }

                this.ws = new WebSocket('ws://localhost:8765');
                this.isReconnecting = true;
                
                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.reconnectAttempts = 0;
                    this.reconnectDelay = 1000;
                    this.isReconnecting = false;
                    this.updateConnectionStatus('Connected');
                    
                    // Send session initialization message
                    this.ws.send(JSON.stringify({
                        type: 'init',
                        session_id: this.sessionId
                    }));
                    
                    // Initialize metrics
                    this.updateMetrics({ 
                        reading_speed: 0, 
                        fixations: 0, 
                        regressions: 0, 
                        dyslexia_probability: 0,
                        indicators: {
                            high_backward_saccades: false,
                            long_fixations: false,
                            irregular_saccades: false,
                            high_blink_rate: false,
                            poor_gaze_stability: false
                        }
                    });
                    
                    // Start sending frames
                    this.isTracking = true;
                    this.startFrameCapture();
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'error') {
                        console.error('Server error:', data.message);
                        this.updateConnectionStatus('Server error: ' + data.message, true);
                        return;
                    }
                    
                    // Update video feed with processed frame if available
                    if (data.processed_frame) {
                        const img = new Image();
                        img.onload = () => {
                            const canvas = document.createElement('canvas');
                            canvas.width = this.videoElement.videoWidth;
                            canvas.height = this.videoElement.videoHeight;
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                            
                            // Create a MediaStream from the canvas
                            const stream = canvas.captureStream();
                            if (this.videoElement.srcObject !== stream) {
                                this.videoElement.srcObject = stream;
                            }
                        };
                        img.src = 'data:image/jpeg;base64,' + data.processed_frame;
                    }
                    
                    this.updateMetrics(data);
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateConnectionStatus('Connection error', true);
                    this.attemptReconnect();
                };

                this.ws.onclose = () => {
                    console.log('WebSocket closed');
                    this.updateConnectionStatus('Disconnected', true);
                    this.stopFrameCapture();
                    if (this.sessionId) {
                        this.attemptReconnect();
                    }
                };
            } catch (error) {
                console.error('Error connecting to WebSocket:', error);
                this.isReconnecting = false;
                this.updateConnectionStatus('Connection failed', true);
                reject(error);
            }
        });
    }

    async attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts || !this.sessionId) {
            console.error('Max reconnection attempts reached or no active session');
            this.stopSession(true);
            return;
        }

        this.reconnectAttempts++;
        this.updateConnectionStatus(`Reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
        
        setTimeout(async () => {
            try {
                await this.connectWebSocket();
            } catch (error) {
                console.error('Reconnection failed:', error);
            }
        }, this.reconnectDelay);
        
        // Exponential backoff
        this.reconnectDelay *= 2;
    }

    startFrameCapture() {
        if (!this.isTracking) return;

        // Create canvas for frame capture
        const canvas = document.createElement('canvas');
        canvas.width = this.videoElement.videoWidth;
        canvas.height = this.videoElement.videoHeight;
        const ctx = canvas.getContext('2d');

        // Send frames every 100ms (10 fps)
        this.frameInterval = setInterval(() => {
            if (!this.isTracking || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
                this.stopFrameCapture();
                return;
            }

            // Draw video frame to canvas
            ctx.drawImage(this.videoElement, 0, 0);

            // Convert to base64 and send
            canvas.toBlob((blob) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64data = reader.result.split(',')[1];
                    this.ws.send(JSON.stringify({
                        type: 'frame',
                        session_id: this.sessionId,
                        frame: base64data
                    }));
                };
                reader.readAsDataURL(blob);
            }, 'image/jpeg', 0.7);
        }, 100);
    }

    stopFrameCapture() {
        if (this.frameInterval) {
            clearInterval(this.frameInterval);
            this.frameInterval = null;
        }
        this.isTracking = false;
    }

    updateMetrics(data) {
        // Update basic metrics
        document.getElementById('readingSpeed').textContent = `Reading Speed: ${data.reading_speed} WPM`;
        document.getElementById('fixations').textContent = `Fixations: ${data.fixations}`;
        document.getElementById('regressions').textContent = `Regressions: ${data.regressions}`;
        document.getElementById('dyslexiaProbability').textContent = `Dyslexia Probability: ${data.dyslexia_probability}%`;

        // Update indicators if available
        if (data.indicators) {
            const indicatorsList = document.getElementById('indicators');
            if (indicatorsList) {
                indicatorsList.innerHTML = Object.entries(data.indicators)
                    .map(([key, value]) => `<li class="${value ? 'active' : ''}">${key.replace(/_/g, ' ')}: ${value ? 'Yes' : 'No'}</li>`)
                    .join('');
            }
        }
    }

    async stopSession(skipServerCall = false) {
        this.stopFrameCapture();

        if (this.sessionId && !skipServerCall) {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                try {
                    this.ws.send(JSON.stringify({
                        type: 'end_session',
                        session_id: this.sessionId
                    }));
                } catch (error) {
                    console.error('Error sending end session message:', error);
                }
            }

            try {
                await fetch(`/api/end-session/${this.sessionId}`, {
                    method: 'POST'
                });
            } catch (error) {
                console.error('Error ending session:', error);
            }
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.videoElement.srcObject = null;
        }

        this.sessionId = null;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.isReconnecting = false;
        this.updateConnectionStatus('Disconnected');
    }

    async startCalibration() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ 
                type: 'calibration_start',
                session_id: this.sessionId
            }));
        }
    }

    async startReadingTest() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ 
                type: 'reading_test_start',
                session_id: this.sessionId
            }));
        }
    }
}

// Initialize the client
const eyeTrackingClient = new EyeTrackingClient();

// Add event listeners to buttons
document.getElementById('startButton').addEventListener('click', () => eyeTrackingClient.startSession());
document.getElementById('stopButton').addEventListener('click', () => eyeTrackingClient.stopSession());
document.getElementById('calibrateButton').addEventListener('click', () => eyeTrackingClient.startCalibration());
document.getElementById('readingTestButton').addEventListener('click', () => eyeTrackingClient.startReadingTest()); 