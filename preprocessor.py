import pandas as pd
import re

def preprocess(data):
    # WhatsApp datetime pattern
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[APM]{2})?\s-\s'

    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Align lengths
    min_len = min(len(messages), len(dates))
    messages = messages[:min_len]
    dates = dates[:min_len]

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert to datetime (try both formats)
    def parse_date(x):
        for fmt in ("%m/%d/%y, %I:%M %p", "%m/%d/%y, %H:%M", "%d/%m/%y, %H:%M", "%d/%m/%y, %I:%M %p"):
            try:
                return pd.to_datetime(x.strip(" -"), format=fmt)
            except Exception:
                continue
        return pd.NaT

    df['message_date'] = df['message_date'].apply(parse_date)
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract user and message
    users, final_messages = [], []
    for message in df['user_message']:
        split_message = message.split(': ', 1)
        if len(split_message) == 2:
            users.append(split_message[0])
            final_messages.append(split_message[1].strip())
        else:
            users.append('group_notification')
            final_messages.append(split_message[0].strip())

    df['user'] = users
    df['message'] = final_messages
    df.drop(columns=['user_message'], inplace=True)

    # Add datetime components
    df['only_date'] =df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
