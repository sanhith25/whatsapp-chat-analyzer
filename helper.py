from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re
import emoji


STOPWORDS_ENGLISH = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours","yourself","yourselves",
    "he","him","his","himself","she","her","hers","herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those",
    "am","is","are","was","were","be","been","being",
    "have","has","had","having","do","does","did","doing",
    "a","an","the","and","but","if","or","because","as","until","while",
    "of","at","by","for","with","about","against","between","into","through","during",
    "before","after","above","below","to","from","up","down","in","out","on","off","over","under",
    "again","further","then","once",
    "here","there","when","where","why","how",
    "all","any","both","each","few","more","most","other","some","such",
    "no","nor","not","only","own","same","so","than","too","very",
    "s","t","can","will","just","don","should","now","ll","re","ve","d","m","o",
    # Chat noise
    "media","omitted","message","deleted","image","video","audio","sticker","gif","photo",
    "group","added","removed","joined","left","http","https","www","com"
}
extract = URLExtract()
def fetch_stats(selected_user, df):
    if selected_user == "Overall":
        temp = df
    else:
        temp = df[df['user'] == selected_user]

    # number of messages
    num_messages = temp.shape[0]

    # number of words
    words = []
    for message in temp['message']:
        words.extend(message.split())
    num_media_messages = temp[temp['message'].str.contains("media omitted", case=False, na=False)].shape[0]
    links = []
    for message in temp['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df: pd.DataFrame):
    temp = df.copy()
    if "group_notification" in temp["user"].unique():
        temp = temp[temp["user"] != "group_notification"]
    user_counts = temp["user"].value_counts()
    x = user_counts.head(5)
    total_msgs = user_counts.sum()
    share = (user_counts / total_msgs * 100).round(2).reset_index()
    share.columns = ["user", "percent"]
    return x, share
def create_wordcloud(selected_user, df):
    temp = df.copy()
    if selected_user != 'Overall':
        temp = temp[temp['user'] == selected_user]

    if 'group_notification' in temp['user'].unique():
        temp = temp[temp['user'] != 'group_notification']

    temp = temp[~temp['message'].str.contains(r'omitted|deleted', case=False, na=False)]

    text = (
        temp['message']
        .dropna()
        .astype(str)
        .str.strip()
        .str.cat(sep=' ')
        .strip()
    )

    if not text:
        return None

    wc = WordCloud(
        width=800,
        height=600,
        min_font_size=10,
        background_color='white',
        collocations=False
    )
    return wc.generate(text)
def most_common_words(selected_user, df, n=20):
    temp = df.copy()

    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]

    if "group_notification" in temp["user"].unique():
        temp = temp[temp["user"] != "group_notification"]

    temp = temp[~temp["message"].str.contains("omitted|deleted", case=False, na=False)]

    words = []
    for message in temp["message"]:
        message = re.sub(r"[^a-zA-Z]", " ", str(message))
        for word in message.lower().split():
            if word not in STOPWORDS_ENGLISH and len(word) > 1:
                words.append(word)

    common_words = Counter(words).most_common(n)
    return pd.DataFrame(common_words, columns=["word", "count"])

## emoji analysis
def emoji_helper(selected_user, df):
    temp = df.copy()

    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]

    if "group_notification" in temp["user"].unique():
        temp = temp[temp["user"] != "group_notification"]

    # extracting emojis
    emojis = []
    for message in temp["message"]:
        for c in str(message):
            if emoji.is_emoji(c):
                emojis.append(c)

    counts = Counter(emojis)
    emoji_df = pd.DataFrame(counts.most_common(len(counts)), columns=["emoji", "count"])
    return emoji_df
def monthly_timeline(selected_user, df):
    temp = df.copy()
    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]
    timeline = temp.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    temp = df.copy()

    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]
    # if date is missing
    if "date" not in temp.columns:
        return pd.DataFrame(columns=["day", "message"])
    # group by calendar day
    daily = (
        temp.dropna(subset=["date"]).groupby(temp["date"].dt.normalize()).size()
            .reset_index(name="message")
    )
    daily.rename(columns={"date": "day"}, inplace=True)
    return daily

def most_busy_day(selected_user, df):
    temp = df.copy()
    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]
    # make sure we have weekday names
    if "weekday" not in temp.columns:
        temp["weekday"] = temp["date"].dt.day_name()

    day_counts = (
        temp.dropna(subset=["date"])
            .groupby("weekday")
            .size()
            .sort_values(ascending=False)
    )
    return day_counts

def most_busy_month(selected_user, df):
    """
    Returns a DataFrame with columns ['month', 'count'],
    sorted by count (descending).
    Assumes preprocessor already created 'month' (full name).
    """
    temp = df.copy()
    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]
    month_counts = (
        temp.dropna(subset=["date"])
            .groupby("month")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .reset_index(drop=True)
    )
    return month_counts

def activity_heatmap(selected_user, df):
    """
    Returns a DataFrame (rows=weekday, cols=hour 0–23) with message counts.
    """
    temp = df.copy()
    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]
    # ensure needed columns
    if "date" not in temp.columns:
        return pd.DataFrame()

    temp = temp.dropna(subset=["date"])
    temp["weekday"] = temp["date"].dt.day_name()
    temp["hour"] = temp["date"].dt.hour
    # pivot: weekday x hour
    heatmap = (
        temp.groupby(["weekday", "hour"]).size().unstack(fill_value=0).reindex(
                ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],fill_value=0))
    # make sure we have all 24 columns
    all_hours = list(range(24))
    heatmap = heatmap.reindex(columns=all_hours, fill_value=0)
    return heatmap


