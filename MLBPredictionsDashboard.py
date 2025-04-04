import streamlit as st
import pandas as pd

# Load CSV file
@st.cache_data
def load_data():
    return pd.read_csv('war.csv')

mlb_data = load_data()

# Function to calculate the sum of ratings by team, excluding selected players (hitters only)
def calculate_team_sum(df, team, excluded_players):
    team_data = df[(df['Team'] == team) & (df['Position'] == 'H')]
    team_data = team_data[~team_data['Name'].isin(excluded_players)]
    return team_data['Rating'].sum()

# Main app structure
st.title("MLB Player WAR Prediction Dashboard")

# Display team options and sum calculations for two teams
st.header("Team Rating Comparison")

# Select two teams to compare
teams = mlb_data['Team'].unique()
team_1 = st.selectbox("Select Team 1", teams)
team_2 = st.selectbox("Select Team 2", teams)

if team_1 and team_2:
    st.write(f"Selected Teams: {team_1} vs {team_2}")

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

    # Calculate hitter-only team sums
    team_1_sum = calculate_team_sum(mlb_data, team_1, excluded_team_1)
    team_2_sum = calculate_team_sum(mlb_data, team_2, excluded_team_2)

    # Allow users to select a pitcher to add to the team sum
    team_1_pitchers = mlb_data[(mlb_data['Team'] == team_1) & (mlb_data['Position'] == 'P')]['Name'].tolist()
    team_2_pitchers = mlb_data[(mlb_data['Team'] == team_2) & (mlb_data['Position'] == 'P')]['Name'].tolist()
    team_1_pitcher = st.selectbox(f"Select a pitcher for {team_1}", team_1_pitchers + ["Other"], key="team_1_pitcher")
    team_2_pitcher = st.selectbox(f"Select a pitcher for {team_2}", team_2_pitchers + ["Other"], key="team_2_pitcher")

    # Get pitcher ratings
    team_1_pitcher_rating = mlb_data.loc[mlb_data['Name'] == team_1_pitcher, 'Rating'].values[0] if team_1_pitcher in team_1_pitchers else 0
    team_2_pitcher_rating = mlb_data.loc[mlb_data['Name'] == team_2_pitcher, 'Rating'].values[0] if team_2_pitcher in team_2_pitchers else 0

    # Calculate final team sums including selected pitchers
    final_team_1_sum = team_1_sum + team_1_pitcher_rating
    final_team_2_sum = team_2_sum + team_2_pitcher_rating

    st.write(f"Total rating for {team_1} (including selected pitcher): {final_team_1_sum:.2f}")
    st.write(f"Total rating for {team_2} (including selected pitcher): {final_team_2_sum:.2f}")

    # Predict matchup outcome
    difference = abs(final_team_1_sum - final_team_2_sum)
    if st.button("Predict Matchup"):
        if final_team_1_sum > final_team_2_sum:
            st.success(f"{team_1} is predicted to win with a difference of {difference:.2f}!")
        elif final_team_1_sum < final_team_2_sum:
            st.success(f"{team_2} is predicted to win with a difference of {difference:.2f}!")
        else:
            st.info("It's a tie!")

# Display top teams by total WAR
st.header("Top Teams by Total WAR")
num_teams = st.slider("Select the number of top teams to display", 1, 30, 10)
team_position_filter = st.radio("Filter teams by player position (for WAR total):", ["All", "H", "P"], index=0)

if team_position_filter != "All":
    position_filtered = mlb_data[mlb_data['Position'] == team_position_filter]
else:
    position_filtered = mlb_data

total_team_ratings = position_filtered.groupby('Team')['Rating'].sum().reset_index()
total_team_ratings = total_team_ratings.sort_values(by='Rating', ascending=False).head(num_teams)
# Reset index and round ratings
total_team_ratings = total_team_ratings.reset_index(drop=True)
total_team_ratings.index += 1
total_team_ratings['Rating'] = total_team_ratings['Rating'].map(lambda x: f"{x:.1f}")
st.table(total_team_ratings)

# Display top players by WAR
st.header("Top Players by WAR")
num_players = st.slider("Select the number of top players to display", 1, 100, 10)
position_filter = st.radio("Filter by position:", ["All", "H", "P"], index=0)
if position_filter != "All":
    filtered_players = mlb_data[mlb_data['Position'] == position_filter]
else:
    filtered_players = mlb_data

top_players = filtered_players.sort_values(by='Rating', ascending=False).head(num_players)
# Reset index and round ratings
top_players = top_players.reset_index(drop=True)
top_players.index += 1
top_players['Rating'] = top_players['Rating'].map(lambda x: f"{x:.1f}")
st.table(top_players[['Name', 'Team', 'Position', 'Rating']])
