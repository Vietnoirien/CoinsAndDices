from coins_and_dices.__main__ import main
from datetime import datetime

def track_game_history(game_type, result, metadata=None):
    """
    Track and store individual game events for analysis
    Parameters:
        game_type (str): Type of game ('dice' or 'coin')
        result (any): Outcome of the game
        metadata (dict): Additional data like bet amount, user choices
    Returns:
        dict: Recorded game event with timestamp
    """
    event = {
        'timestamp': datetime.now(),
        'game_type': game_type,
        'result': result,
        'metadata': metadata or {}
    }
    return event

def calculate_odds(event_type, parameters):
    """
    Calculate probability for specific game events
    Parameters:
        event_type (str): Type of probability to calculate ('dice' or 'coin')
        parameters (dict): Event-specific parameters
    Returns:
        float: Probability of the specified event
    """
    if event_type == 'standard_dice':
        target = parameters.get('target')
        sides = parameters.get('sides', 6)
        return target/sides
    elif event_type == 'coin':
        return 0.5
    return 0.0

def generate_game_report(session_data):
    """
    Generate detailed report of gaming session
    Parameters:
        session_data (dict): Collection of game results and statistics
    Returns:
        dict: Formatted report with analysis and insights
    """
    report = {
        'total_games': len(session_data),
        'games_by_type': {
            'standard_dice': sum(1 for game in session_data if game['game_type'] == 'standard_dice'),
            'coin': sum(1 for game in session_data if game['game_type'] == 'coin'),
            'runebound': sum(1 for game in session_data if game['game_type'] == 'runebound'),
            'custom_dice': sum(1 for game in session_data if game['game_type'] == 'custom_dice')
        },
        'session_duration': calculate_session_duration(session_data),
        'win_loss_ratio': calculate_win_loss_ratio(session_data),
        'trends': analyze_trends(session_data)
    }
    return report

def calculate_session_duration(session_data):
    """
    Calculate total duration of gaming session
    Parameters:
        session_data (list): List of game events with timestamps
    Returns:
        float: Duration in minutes
    """
    if not session_data:
        return 0.0
        
    start_time = min(event['timestamp'] for event in session_data)
    end_time = max(event['timestamp'] for event in session_data)
    duration = (end_time - start_time).total_seconds() / 60
    return round(duration, 2)

def calculate_win_loss_ratio(session_data):
    """
    Calculate ratio of wins to losses across all games
    Parameters:
        session_data (list): List of game events with results
    Returns:
        dict: Win-loss statistics including ratio
    """
    wins = sum(1 for game in session_data if game['metadata'].get('won', False))
    total = len(session_data)
    losses = total - wins
    
    return {
        'wins': wins,
        'losses': losses,
        'ratio': round(wins/total, 2) if total > 0 else 0.0
    }

def analyze_trends(session_data):
    """
    Analyze gaming patterns and trends
    Parameters:
        session_data (list): List of game events
    Returns:
        dict: Trend analysis results
    """
    trends = {
        'streak': calculate_longest_streak(session_data),
        'favorite_game': get_most_played_game(session_data),
        'hourly_activity': get_hourly_distribution(session_data)
    }
    return trends

def calculate_longest_streak(session_data):
    """
    Find longest winning streak
    """
    current_streak = max_streak = 0
    
    for game in session_data:
        if game['metadata'].get('won', False):
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
            
    return max_streak

def get_most_played_game(session_data):
    """
    Determine most frequently played game type
    """
    game_counts = {'standard_dice': 0, 'custom_dice': 0, 'coin': 0, 'runebound': 0}
    for game in session_data:
        game_counts[game['game_type']] += 1
    
    return max(game_counts.items(), key=lambda x: x[1])[0]

def get_hourly_distribution(session_data):
    """
    Get distribution of games played by hour
    """
    hourly = {i: 0 for i in range(24)}
    for game in session_data:
        hour = game['timestamp'].hour
        hourly[hour] += 1
    
    return hourly

if __name__ == '__main__':
    main()
