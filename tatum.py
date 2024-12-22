```python
import pandas as pd
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import plotly.graph_objs as go
import warnings

warnings.filterwarnings("ignore")

# Player IDs
player_ids = [
    1629029, 203954, 203999, 203507, 1628983, 203076, 2544, 1627734, 201142, 1626164,
    1628973, 1629027, 1628378, 1629630, 1641705, 1630169, 202681, 1628368, 1630163,
    1630178, 1630162, 201939, 202695, 203944, 1630578, 203081, 1630567, 1629627,
    201942, 1627749, 1630217, 1628374, 1630595, 1628389, 1627783, 1627750, 1631094,
    1626157, 202331, 1627759, 202710, 1628398, 1627742, 202696, 204001, 201935,
    1628386, 1628970, 1627832, 1629014, 1628991, 1629028, 1630596, 203468, 203497,
    1631114, 1626179, 1629639, 1631096, 1630552, 1630532, 203078, 1626156, 1629632,
    1631105, 203897, 1629628, 1630170, 202699, 1630560, 1628969, 1629636, 1626167,
    1628401, 1630224, 203924, 1629012, 1630559, 1629651, 203994, 203114, 1630193,
    1629008, 1630166, 1631109, 1628381, 1627763, 203932, 1627751, 1626145, 203991,
    201950, 203903, 1629655, 203992, 1629673, 1627826, 1628370, 202685
]

def calculate_basic_and_per_for_season(player_data, season="2023-24"):
    player_id = player_data['id']
    player_name = player_data['full_name']

    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    data_frames = career_stats.get_data_frames()
    relevant_data = pd.DataFrame()
    for df in data_frames:
        if "SEASON_ID" in df.columns:
            relevant_data = pd.concat([relevant_data, df[df["SEASON_ID"] == season]])
    if relevant_data.empty:
        print(f"Data not available for player {player_id} in season {season}")
        return None

    total_fgm = relevant_data["FGM"].sum()
    total_fga = relevant_data["FGA"].sum()
    total_fg3m = relevant_data["FG3M"].sum()
    total_fta = relevant_data["FTA"].sum()
    total_ftm = relevant_data["FTM"].sum()
    total_pts = relevant_data["PTS"].sum()
    total_reb = relevant_data["REB"].sum()
    total_ast = relevant_data["AST"].sum()
    total_stl = relevant_data["STL"].sum()
    total_blk = relevant_data["BLK"].sum()
    total_tov = relevant_data["TOV"].sum()
    total_mp = relevant_data["MIN"].sum()
    games_played = len(relevant_data)
    ts = (total_fgm + (0.5 * total_fg3m)) / total_fga if total_fga > 0 else 0
    per = (total_pts + total_reb + total_ast + total_stl + total_blk) / total_mp - \
          (total_fga - total_fgm + total_tov + total_fta - total_ftm) / total_mp
    pst_reb_ast = total_pts + total_reb + total_ast

    metrics = {
        "Player ID": player_id,
        "Player Name": player_name,
        "Season": season,
        "Games Played": games_played,
        "True Shooting Percentage": ts,
        "Simplified PER": per,
        "PST_REB_AST": pst_reb_ast
    }
    return metrics

def create_bar_graph(x_data, y_data, x_label, y_label, title):
    trace = go.Bar(
        x=x_data,
        y=y_data,
        marker=dict(color='rgb(26, 118, 255)'),
        opacity=0.6
    )
    layout = go.Layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label)
    )
    fig = go.Figure(data=[trace], layout=layout)
    fig.show()

def create_radar_chart(player_names, values, title):
    data = [go.Scatterpolar(
        r=values[i],
        theta=['True Shooting Percentage', 'Simplified PER', 'PST_REB_AST'],
        fill='toself',
        name=player_names[i]
    ) for i in range(len(player_names))]

    layout = go.Layout(
        title=title,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([max(val) for val in values])]
            )
        ),
        showlegend=True
    )

    fig = go.Figure(data=data, layout=layout)
    fig.show()

jayson_tatum_id = 1628369
# Getting players data
playerz = players.get_players()
jayson_tatum_data = next((player for player in playerz if player['id'] == jayson_tatum_id), None)
other_players_data = [player for player in playerz if player['id'] in player_ids]

# Combining Jayson Tatum data with other players' data
all_players_data = [jayson_tatum_data] + other_players_data

# Calculate metrics for Jayson Tatum
jayson_metrics = calculate_basic_and_per_for_season(jayson_tatum_data)

if jayson_metrics:
    print(f"Player ID: {jayson_metrics['Player ID']}")
    print(f"Player Name: {jayson_metrics['Player Name']}")
    print(f"Season: {jayson_metrics['Season']}")
    print(f"True Shooting Percentage: {jayson_metrics['True Shooting Percentage']:.2f}")
    print(f"Simplified PER: {jayson_metrics['Simplified PER']:.2f}")
    print(f"PST_REB_AST: {jayson_metrics['PST_REB_AST']}")

# Calculate metrics for other players
comparison_data = []
comparison_data.append(jayson_metrics)

i = 1
for player in other_players_data:
    data = calculate_basic_and_per_for_season(player)
    if data:
        if data['Simplified PER'] < jayson_metrics['Simplified PER'] and \
           data['True Shooting Percentage'] < jayson_metrics['True Shooting Percentage'] and \
           data['PST_REB_AST'] < jayson_metrics['PST_REB_AST']:
            comparison_data.append(data)
            print(f"Player {i} of {len(other_players_data)}")
            i += 1

# Adding Jayson Tatum's metrics to comparison data

# Comparing True Shooting Percentage (TS%)
ts_data = [{"Player Name": data["Player Name"], "TS%": data["True Shooting Percentage"]} for data in comparison_data]
ts_data.sort(key=lambda x: x["TS%"], reverse=True)
ts_players = [data["Player Name"] for data in ts_data]
ts_values = [data["TS%"] for data in ts_data]
ts_title = "True Shooting Percentage Comparison"

create_bar_graph(ts_players, ts_values, "Player Name", "TS%", ts_title)

# Comparing Simplified PER
per_data = [{"Player Name": data["Player Name"], "Simplified PER": data["Simplified PER"]} for data in comparison_data]
per_data.sort(key=lambda x: x["Simplified PER"], reverse=True)
per_players = [data["Player Name"] for data in per_data]
per_values = [data["Simplified PER"] for data in per_data]
per_title = "Simplified PER Comparison"

create_bar_graph(per_players, per_values, "Player Name", "Simplified PER", per_title)

# Comparing PST_REB_AST
pst_reb_ast_data = [{"Player Name": data["Player Name"], "PST_REB_AST": data["PST_REB_AST"]} for data in comparison_data]
pst_reb_ast_data.sort(key=lambda x: x["PST_REB_AST"], reverse=True)
pst_reb_ast_players = [data["Player Name"] for data in pst_reb_ast_data]
pst_reb_ast_values = [data["PST_REB_AST"] for data in pst_reb_ast_data]
pst_reb_ast_title = "PST_REB_AST Comparison"

create_bar_graph(pst_reb_ast_players, pst_reb_ast_values, "Player Name", "PST_REB_AST", pst_reb_ast_title)

# Comparing multiple metrics with radar chart
player_names = [data["Player Name"] for data in comparison_data]
values = [[data["True Shooting Percentage"], data["Simplified PER"], data["PST_REB_AST"]] for data in comparison_data]
radar_title = "Comparison of Metrics"

create_radar_chart(player_names, values, radar_title)
```