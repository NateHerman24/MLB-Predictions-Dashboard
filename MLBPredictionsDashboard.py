import streamlit as st
import pandas as pd

# App Config
st.set_page_config(page_title="MLB WAR Predictions", layout="wide")
st.title("⚾ MLB WAR Predictions Dashboard")

# Load CSV file
@st.cache_data
def load_data():
    return pd.read_csv('war.csv')

mlb_data = load_data()

# Helper functions
def calculate_team_sum(df, team, excluded_players):
    team_data = df[(df['Team'] == team) & (df['Position'] == 'H')]
    team_data = team_data[~team_data['Name'].isin(excluded_players)]
    return team_data['Rating'].sum()

# Tabs
tab1, tab2 = st.tabs(["Compare Teams", "Rankings"])

# --- Compare Teams ---
with tab1:
    st.header("Team Rating Comparison")
    teams = sorted(mlb_data['Team'].unique())

    col1, col2 = st.columns(2)
    with col1:
        team_1 = st.selectbox("Select Team 1", teams)
    with col2:
        team_2 = st.selectbox("Select Team 2", teams)

    # Allow users to exclude players from Team 1 and Team 2 (hitters only)
    excluded_team_1 = st.multiselect(
        f"Exclude hitters from {team_1}", 
        mlb_data[(mlb_data['Team'] == team_1) & (mlb_data['Position'] == 'H')]['Name'].tolist(),
        key="excluded_team_1"
    )
    excluded_team_2 = st.multiselect(
        f"Exclude hitters from {team_2}", 
        mlb_data[(mlb_data['Team'] == team_2) & (mlb_data['Position'] == 'H')]['Name'].tolist(),
        key="excluded_team_2"
    )

    # Allow users to select a pitcher to add to the team sum
    team_1_sum = calculate_team_sum(mlb_data, team_1, excluded_team_1)
    team_2_sum = calculate_team_sum(mlb_data, team_2, excluded_team_2)

    # Allow users to select a pitcher to add to the team sum
    team_1_pitchers = mlb_data[(mlb_data['Team'] == team_1) & (mlb_data['Position'] == 'P')]['Name'].tolist()
    team_2_pitchers = mlb_data[(mlb_data['Team'] == team_2) & (mlb_data['Position'] == 'P')]['Name'].tolist()

    col1, col2 = st.columns(2)
    with col1:
        team_1_pitcher = st.selectbox(f"Select a pitcher for {team_1}", team_1_pitchers + ["Other"], key="team_1_pitcher")
    with col2:
        team_2_pitcher = st.selectbox(f"Select a pitcher for {team_2}", team_2_pitchers + ["Other"], key="team_2_pitcher")

    # Get pitcher ratings
    team_1_pitcher_rating = mlb_data.loc[mlb_data['Name'] == team_1_pitcher, 'Rating'].values[0] if team_1_pitcher in team_1_pitchers else 0
    team_2_pitcher_rating = mlb_data.loc[mlb_data['Name'] == team_2_pitcher, 'Rating'].values[0] if team_2_pitcher in team_2_pitchers else 0

    # Calculate final team sums including selected pitchers
    final_team_1_sum = team_1_sum + team_1_pitcher_rating
    final_team_2_sum = team_2_sum + team_2_pitcher_rating

    st.metric(f"{team_1} Total WAR", round(final_team_1_sum, 1))
    st.metric(f"{team_2} Total WAR", round(final_team_2_sum, 1))

    if st.button("Predict Matchup"):
        if final_team_1_sum > final_team_2_sum:
            st.success(f"{team_1} is predicted to win by {abs(final_team_1_sum - final_team_2_sum):.1f} WAR!")
        elif final_team_2_sum > final_team_1_sum:
            st.success(f"{team_2} is predicted to win by {abs(final_team_2_sum - final_team_1_sum):.1f} WAR!")
        else:
            st.info("It's a tie!")

# --- Rankings ---
with tab2:
    st.header("Top Teams and Players by WAR")

    ranking_option = st.selectbox("Select Ranking Type", ["Team Rankings", "Player Rankings"])

    if ranking_option == "Team Rankings":
        num_teams = st.slider("Select the number of top teams to display", 1, 30, 10)
        team_position_filter = st.radio("Filter teams by player position (for WAR total):", ["All", "H", "P"], index=0)

        if team_position_filter != "All":
            position_filtered = mlb_data[mlb_data['Position'] == team_position_filter]
        else:
            position_filtered = mlb_data

        team_war = position_filtered.groupby('Team')['Rating'].sum().reset_index()
        team_war = team_war.sort_values(by='Rating', ascending=False).head(num_teams)
        team_war = team_war.reset_index(drop=True)
        team_war.index += 1
        team_war['Rating'] = team_war['Rating'].map(lambda x: f"{x:.1f}")
        st.table(team_war.rename(columns={'Rating': 'Total Hitter WAR'}))

    else:
        num_players = st.slider("Select the number of top players to display", 1, 100, 10)
        position_filter = st.radio("Filter by position:", ["All", "H", "P"], index=0)

        if position_filter != "All":
            filtered_players = mlb_data[mlb_data['Position'] == position_filter]
        else:
            filtered_players = mlb_data

        player_rankings = filtered_players.sort_values(by='Rating', ascending=False).head(num_players)
        player_rankings = player_rankings.reset_index(drop=True)
        player_rankings.index += 1
        player_rankings['Rating'] = player_rankings['Rating'].map(lambda x: f"{x:.1f}")
        st.table(player_rankings[['Name', 'Team', 'Position', 'Rating']])

