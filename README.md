# Study MCP Server

A Python-based Model Context Protocol (MCP) server for comprehensive study data management. This server provides tools for managing Eisenhower Matrix tasks, daily study data, statistics analytics, and Pomodoro sessions through Firebase Firestore.

## Features

### 📋 Eisenhower Matrix Management
- **Get Tasks**: Retrieve all tasks organized by priority quadrants
- **Save Tasks**: Store and update task lists with status tracking
- **Quadrants**: HUHI (High Urgent High Important), LUHI, HULI, LULI

### 📊 Daily Data Tracking
- **Monthly Data**: Retrieve daily study data for specific months
- **Save Daily Data**: Record daily study emotions and summaries
- **Emotions**: RELAXED, BALANCED, FOCUSED, INTENSE, OVERWHELMED, BURNT_OUT

### 📈 Statistics & Analytics
- **Monthly Overview**: Comprehensive statistics including:
  - Study overview (days, hours, streaks)
  - Emotional trends and distribution
  - Productivity metrics and completion rates
  - Quadrant performance analysis
  - Pomodoro insights

### 🍅 Pomodoro Session Management
- **Analytics**: Get detailed Pomodoro session analytics
- **Save Sessions**: Record work/break durations and completion status
- **Preset Tracking**: Monitor effectiveness of different presets

## Installation

### Prerequisites
- Python 3.8+
- Firebase project with Firestore enabled
- Firebase service account key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd study-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your Firebase credentials:
   ```env
   SERVICE_ACCOUNT_KEY_PATH=/path/to/your/firebase-service-account-key.json
   FIREBASE_PROJECT_ID=your-firebase-project-id
   ```

4. **Firebase Setup**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Create a new project or select existing one
   - Go to Project Settings → Service Accounts
   - Click "Generate new private key"
   - Save the JSON file and update the path in `.env`
   - Enable Firestore Database in your Firebase project

## Usage

### Running the Server

```bash
# Make the main module executable
chmod +x src/main.py

# Run the server
python src/main.py
```

### Testing with MCP Inspector

1. **Install MCP Inspector**
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Run with Inspector**
   ```bash
   mcp-inspector python src/main.py
   ```

3. **Alternative method**
   ```bash
   mcp-inspector --command "python" --args "src/main.py"
   ```

### Available Tools

The server provides 7 tools for comprehensive study management:

#### Eisenhower Matrix
- `eisenhower_get_tasks` - Retrieve all tasks for a user
- `eisenhower_save_tasks` - Save/update task lists

#### Daily Data
- `daily_data_get_monthly` - Get daily data for a specific month
- `daily_data_save` - Save daily study data entry

#### Statistics
- `stats_monthly_overview` - Get comprehensive monthly statistics

#### Pomodoro
- `pomodoro_get_analytics` - Get Pomodoro session analytics
- `pomodoro_save_session` - Save a Pomodoro session

## Example Usage

### Get Tasks
```json
{
  "name": "eisenhower_get_tasks",
  "arguments": {
    "userId": "user-123"
  }
}
```

### Save Daily Data
```json
{
  "name": "daily_data_save",
  "arguments": {
    "userId": "user-123",
    "day": 15,
    "month": 12,
    "year": 2024,
    "emoji": "FOCUSED",
    "summary": "Great study session today!"
  }
}
```

### Get Monthly Statistics
```json
{
  "name": "stats_monthly_overview",
  "arguments": {
    "userId": "user-123",
    "year": 2024,
    "month": 12
  }
}
```

## Project Structure

```
study-mcp-server/
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
├── README.md               # This file
└── src/
    ├── __init__.py
    ├── main.py             # Main server entry point
    ├── config.py           # Configuration management
    ├── firebase_client.py  # Firebase initialization
    └── tools/
        ├── __init__.py
        ├── eisenhower.py   # Task management tools
        ├── daily_data.py   # Daily data tools
        ├── stats.py        # Statistics tools
        └── pomodoro.py     # Pomodoro session tools
```

## Data Structure

### Firebase Collections
- `users/{userId}/tasks` - Eisenhower Matrix tasks
- `users/{userId}/dailyData` - Daily study data
- `users/{userId}/pomodoroSessions` - Pomodoro session records

### Task Schema
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "quadrant": "HUHI|LUHI|HULI|LULI",
  "status": "created|in_progress|completed",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```

### Daily Data Schema
```json
{
  "day": "number",
  "month": "number", 
  "year": "number",
  "emoji": "RELAXED|BALANCED|FOCUSED|INTENSE|OVERWHELMED|BURNT_OUT",
  "summary": "string"
}
```

## Error Handling

The server includes comprehensive error handling:
- Firebase initialization errors
- Invalid tool parameters
- Database operation failures
- Network connectivity issues

All errors are returned as JSON responses with descriptive error messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

This project is part of the larger Sahay ecosystem. Here are the other components:

### Backend Services
- **[Backend API](https://github.com/StraightOuttaVellore-Google/google-hackathon-backend)** - FastAPI backend with RESTful APIs and WebSocket support

### Frontend Applications
- **[Frontend App](https://github.com/StraightOuttaVellore-Google/google-hackathon-frontend)** - React frontend for the complete wellness platform
- **[Voice Agent](https://github.com/StraightOuttaVellore-Google/VoiceAgentGeminiLive)** - Real-time voice journaling with Google Gemini Live API

### AI & Wellness Agents
- **[ADK Wellness Bots](https://github.com/StraightOuttaVellore-Google/adk-mas-healthcare)** - AI-powered wellness agents using Google's Agent Development Kit

### Additional Features
- **[Discord Fullstack](https://github.com/StraightOuttaVellore-Google/discord-fullstack)** - Neumorphic Discord-style chat application
- **[Sahay Aura Glow](https://github.com/StraightOuttaVellore-Google/sahay-aura-glow)** - Complete voice journaling application with advanced features

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run integration tests
pytest tests/integration/
```

### Test Coverage
- Unit tests for all tool functions
- Integration tests for Firebase operations
- Error handling validation
- Data validation testing
- Performance testing

## 🚀 Deployment

### Production Setup
1. **Environment Configuration**:
   ```bash
   export SERVICE_ACCOUNT_KEY_PATH="/path/to/firebase-key.json"
   export FIREBASE_PROJECT_ID="your-project-id"
   export ENVIRONMENT="production"
   ```

2. **Docker Deployment**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "src/main.py"]
   ```

3. **Cloud Deployment**:
   - Google Cloud Run
   - AWS Lambda
   - Azure Container Instances
   - Railway

## 📊 Performance

### Optimization Features
- **Connection Pooling**: Efficient Firebase connection management
- **Batch Operations**: Optimized database operations
- **Caching**: Smart caching for frequently accessed data
- **Error Recovery**: Automatic retry mechanisms for failed operations

### Monitoring
- **Database Metrics**: Track Firestore operation performance
- **Error Rates**: Monitor and alert on operation failures
- **Response Times**: Track tool execution performance
- **Resource Usage**: Monitor memory and CPU usage

## 🔒 Security

### Security Features
- **Firebase Security Rules**: Proper access control and data validation
- **API Key Protection**: Secure handling of Firebase credentials
- **Input Validation**: Comprehensive validation of all inputs
- **Error Handling**: Secure error messages without sensitive data

### Data Protection
- **Encryption**: All data encrypted in transit and at rest
- **Access Control**: User-based data isolation
- **Audit Logging**: Comprehensive logging for compliance
- **Data Retention**: Configurable data retention policies

## 🛠️ Development

### Project Structure
```
study-mcp-server/
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
├── README.md               # This file
├── setup.py                # Package setup
└── src/
    ├── __init__.py
    ├── main.py             # Main server entry point
    ├── config.py           # Configuration management
    ├── firebase_client.py  # Firebase initialization
    └── tools/
        ├── __init__.py
        ├── eisenhower.py   # Task management tools
        ├── daily_data.py   # Daily data tools
        ├── stats.py        # Statistics tools
        └── pomodoro.py     # Pomodoro session tools
```

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes
- Ensure Firebase security rules are maintained

## 📈 Analytics & Insights

### Available Analytics
- **Study Patterns**: Track study habits and productivity trends
- **Emotional Trends**: Monitor emotional states and patterns
- **Task Performance**: Analyze task completion and prioritization
- **Pomodoro Effectiveness**: Measure focus session productivity

### Data Visualization
- Monthly overview charts
- Emotional state distributions
- Task completion rates
- Productivity metrics
- Study streak tracking

## 🔧 Configuration

### Environment Variables
- `SERVICE_ACCOUNT_KEY_PATH`: Path to Firebase service account key
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `ENVIRONMENT`: Environment (development/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

### Firebase Setup
1. **Project Configuration**:
   - Create Firebase project
   - Enable Firestore Database
   - Set up security rules
   - Generate service account key

2. **Security Rules**:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId}/{document=**} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
     }
   }
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting
- Be respectful and constructive in discussions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Firebase team for the excellent database service
- Model Context Protocol for the standardized interface
- Python community for various libraries
- The open-source community for tools and inspiration

## 📞 Support

For support and questions:
1. Check the [documentation](https://github.com/StraightOuttaVellore-Google/sahay-mcp-server/wiki)
2. Open an issue in the GitHub repository
3. Contact the development team

---

**Sahay MCP Server** - Empowering study management through intelligent data tools 📚✨
