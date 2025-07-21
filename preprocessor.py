import re
import pandas as pd
from datetime import datetime

def preprocess(data):
    # Updated regex to match date format like '29/02/24, 1:39 pm - '
    pattern = r'(\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}[  ]?(?:am|pm|AM|PM))\s-\s'

    # Extract messages and corresponding dates
    messages = re.split(pattern, data)[1:]
    dates = messages[::2]  # Even indices: date strings
    messages = messages[1::2]  # Odd indices: actual messages

    cleaned_dates = []
    for date_str in dates:
        # Replace narrow no-break space (U+202F) or any weird spaces with a normal space
        date_str = re.sub(r'[ ]', ' ', date_str)
        # Parse the datetime object correctly
        date_obj = datetime.strptime(date_str.strip(), '%d/%m/%y, %I:%M %p')
        cleaned_dates.append(date_obj)

    df = pd.DataFrame({'user_message': messages, 'date': cleaned_dates})

    # Split username and message
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if len(entry) >= 3:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Add additional time-based columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create hourly period range
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour+1}")
    df['period'] = period

    return df
