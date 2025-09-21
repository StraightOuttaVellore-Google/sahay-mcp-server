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

## Support

For issues and questions:
1. Check the existing issues
2. Create a new issue with detailed description
3. Include error logs and environment details
