import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import emoji as emoji_lib
import matplotlib.dates as mdates


import preprocessor, helper

# ---------- Page setup ----------
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("📱 WhatsApp Chat Analyzer")
st.caption("Upload your exported chat file to view summary stats and participation insights.")

# ---------- Emoji font utilities (Windows-friendly) ----------
EMOJI_FONTS = [
    "Segoe UI Emoji",       # Windows
    "Apple Color Emoji",    # macOS (in case you run elsewhere)
    "Noto Color Emoji",     # Linux
    "Noto Emoji",
    "Twemoji Mozilla",
    "Symbola",
]

def pick_emoji_font():
    """
    Try to set a system emoji font for Matplotlib.
    Returns the chosen font name, or None if not found.
    """
    for name in EMOJI_FONTS:
        try:
            path = fm.findfont(name, fallback_to_default=False)
            if path:
                plt.rcParams["font.family"] = name
                plt.rcParams["font.sans-serif"] = [name]
                return name
        except Exception:
            pass
    return None

def strip_vs16(s: str) -> str:
    """Remove emoji variation selector-16 to avoid tofu boxes on some fonts."""
    return s.replace("\ufe0f", "")

# ---------- Sidebar ----------
st.sidebar.title("Controls")
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file (.txt)")

# ---------- Body ----------
if uploaded_file is None:
    st.info("👈 Upload a chat file to begin.")
else:
    # Read & preprocess
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8", errors="ignore")
    df = preprocessor.preprocess(data)  # expected to return DataFrame with ['user','message',...]

    user_list = df["user"].unique().tolist()
    if "group_notification" in user_list:
        user_list.remove("group_notification")
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Analyze for", user_list)
    show_btn = st.sidebar.button("Show analysis")

    if show_btn:
        #  Stats row
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.subheader("Summary")
        st.caption(f"High-level stats for **{selected_user}**")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(label="Total messages", value=num_messages)
        with c2:
            st.metric(label="Total words", value=words)
        with c3:
            st.metric(label="Media shared", value=num_media_messages)
        with c4:
            st.metric(label="Links shared", value=num_links)

        st.divider()

        ## timeline
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], marker='o')
        plt.xticks(rotation="vertical")
        if selected_user == "Overall":
            ax.set_title("Monthly Timeline (Overall)")
        else:
            ax.set_title(f"Monthly Timeline — {selected_user}")

        ax.set_xlabel("Month")
        ax.set_ylabel("Messages")

        st.pyplot(fig)

        # ---------- Daily Timeline ----------
        st.divider()
        st.subheader("Daily Timeline")
        daily = helper.daily_timeline(selected_user, df)
        if daily.empty:
            st.info("No daily data to display for this selection.")
        else:
            fig, ax = plt.subplots()
            ax.plot(daily["day"], daily["message"], marker="o", linewidth=1)
            # Date formatting
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %Y"))
            plt.xticks(rotation='vertical')
            # Titles/labels
            ax.set_title("Daily Timeline (Overall)" if selected_user == "Overall"
                         else f"Daily Timeline — {selected_user}")
            ax.set_xlabel("Day")
            ax.set_ylabel("Messages")

            st.pyplot(fig, use_container_width=True)

        # ---------- Most busy users (only for Overall) ----------
        if selected_user == "Overall":
            st.subheader("Most Busy Users")
            st.caption("Top contributors by message count and their share of total conversation.")

            x, new_df = helper.most_busy_users(df)

            # Layout: chart on the left, table on the right
            left, right = st.columns([2, 1], gap="large")

            with left:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values)
                ax.set_title("Messages by User")
                ax.set_xlabel("User")
                ax.set_ylabel("Messages")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)

            with right:
                st.markdown("**User Activity Summary**")
                st.dataframe(new_df, use_container_width=True)

        # ---------- Activity Map ----------
        st.divider()
        st.subheader("Activity Map")
        col_day, col_month = st.columns(2, gap="large")
        # Most busy day
        with col_day:
            st.markdown("**Most busy day**")
            day_counts = helper.most_busy_day(selected_user, df)

            if day_counts.empty:
                st.info("No day-wise activity to display.")
            else:
                fig1, ax1 = plt.subplots()
                ax1.bar(day_counts.index, day_counts.values)
                ax1.set_xlabel("Day of week")
                ax1.set_ylabel("Messages")
                ax1.set_title("Most busy day")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig1, use_container_width=True)
        # Most busy month
        with col_month:
            st.markdown("**Most busy month**")
            month_counts = helper.most_busy_month(selected_user, df)

            if month_counts.empty:
                st.info("No month-wise activity to display.")
            else:
                fig2, ax2 = plt.subplots()
                ax2.bar(month_counts["month"], month_counts["count"])
                ax2.set_xlabel("Month")
                ax2.set_ylabel("Messages")
                ax2.set_title("Most busy month")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig2, use_container_width=True)

        # ---------- Weekly Activity Heatmap ----------
        st.divider()
        st.subheader("Weekly Activity Heatmap")
        hm = helper.activity_heatmap(selected_user, df)
        if hm.empty:
            st.info("No activity data available to build the heatmap.")
        else:
            fig, ax = plt.subplots()
            # draw heatmap
            im = ax.imshow(hm.values, aspect="auto")
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label("Messages", rotation=90)
            # ticks & labels
            ax.set_yticks(range(len(hm.index)))
            ax.set_yticklabels(hm.index)
            ax.set_xticks(range(24))
            ax.set_xticklabels(range(24))
            # titles/labels
            ax.set_xlabel("Hour of day (0–23)")
            ax.set_ylabel("Weekday")
            ax.set_title("Activity Heatmap (Overall)" if selected_user == "Overall"
                         else f"Activity Heatmap — {selected_user}")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

        # ---------- Word Cloud ----------
        st.divider()
        st.subheader("Word Cloud")
        st.caption("Overall" if selected_user == "Overall" else f"For: {selected_user}")

        wc_img = helper.create_wordcloud(selected_user, df)

        if wc_img is None:
            st.info("No textual messages to generate a word cloud (likely only media/deleted/system messages).")
        else:
            fig, ax = plt.subplots()
            ax.imshow(wc_img)
            ax.axis("off")
            st.pyplot(fig, use_container_width=True)

        # ---------- Most Common Words ----------
        st.divider()
        st.subheader("Most Common Words")
        st.caption("Based on text content (ignores stopwords, media, and deleted messages).")

        top_n = st.slider("Select number of top words", 5, 40, 20, key="top_words")
        common_df = helper.most_common_words(selected_user, df, n=top_n)

        if common_df.empty:
            st.info("No words to display for this selection.")
        else:
            st.dataframe(common_df, use_container_width=True)
            fig, ax = plt.subplots()
            ax.barh(common_df["word"][::-1], common_df["count"][::-1])
            ax.set_xlabel("Count")
            ax.set_ylabel("Word")
            ax.set_title("Most Common Words (Overall)" if selected_user == "Overall" else f"Most Common Words — {selected_user}")
            st.pyplot(fig, use_container_width=True)

        # Emoji Analysis
        st.divider()
        st.subheader("Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        if emoji_df.empty:
            st.info("No emojis found for this selection.")
        else:
            st.dataframe(emoji_df, use_container_width=True)

            # Top 10 emoji bar chart with emoji-capable font (Windows: Segoe UI Emoji)
            top_emojis = emoji_df.head(10)
            font_used = pick_emoji_font()

            # labels: try real emoji if we have a proper font, else demojized names
            labels = [strip_vs16(e) for e in top_emojis["emoji"]]
            if not font_used:
                labels = [emoji_lib.demojize(e) for e in top_emojis["emoji"]]

            fig, ax = plt.subplots()
            ax.bar(labels, top_emojis["count"])
            ax.set_title("Top Emojis")
            plt.xticks(rotation=0)
            st.pyplot(fig, use_container_width=True)
