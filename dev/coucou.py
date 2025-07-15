import plotly.graph_objects as go
import plotly.offline as pyo
import numpy as np
import pandas as pd
import pathlib
import json

# Your data loading
# current_directory = pathlib.Path.cwd()
parent_path = pathlib.Path(__file__).parent.parent
df = pd.read_excel(parent_path / "Results" / "Tableaux" / "Feelings" / "Feelings.xlsx", index_col=[0, 1])
et = pd.read_excel(parent_path / "Files" / "ET_modified.xlsx", usecols="B:C, F:L, P:AO, AQ:AW, BC: BE", skiprows=6)
hex = pd.read_excel(parent_path / "Files" / "code_hex.xlsx", sheet_name="Données Complètes palettes", index_col="Nom Teinte")


# On récupère les lignes concernant P2d comme pour l'autre fichier
et_p2d = et.loc[et.loc[:, "Parent Label"].str.contains("P2d", na=False), :]

feelings = list(df.index.get_level_values(0).unique())
colors = ["Reds", "Greens", "Oranges", "Yellows", "Whites", "Lavenders", "Blues"]
codes_hex = ["#EDCCD5", "#C3E9CB", "#F7D0B7", "#FFEEC4", "#F9F9FA", "#D9C8E5", "#C0E3F6"]

df_feeling = df.loc[feelings[0], :]
et_p2d_feelings = et_p2d.loc[et_p2d.loc[:, "Parent Label"].str.contains(feelings[0]), :]
et_p2d_feelings["Label_modified"] = et_p2d_feelings["Label_modified"].str.split("_").str[-1]
et_p2d_feelings = et_p2d_feelings.set_index("Label_modified")

hex_bis = hex[hex.index.isin(et_p2d_feelings.index)]
hex_bis = hex_bis.reindex(et_p2d_feelings.index)
colors_shades = hex_bis["HEX"].tolist()

for i, color in enumerate(colors):
    df_feeling.loc[color, "Code_hex"] = codes_hex[i]
groups = df_feeling.index

# Generate data
np.random.seed(42)
all_data = {}

for i, group in enumerate(groups):
    center_x = df_feeling.loc[group, "Respondent count (fixation dwells)"]
    center_y = df_feeling.loc[group, "Dwell time (fixation, ms)"]
    
    np.random.seed(42 + i * 100)
    n_points = 60 + i * 10
    # detail_x = np.random.randn(n_points) * 1.2 + center_x
    # detail_y = np.random.randn(n_points) * 1.2 + center_y
    detail_x = et_p2d_feelings.loc[et_p2d_feelings.loc[:, "Parent Label"].str.contains(group), "Respondent count (fixation dwells)"]
    detail_y = et_p2d_feelings.loc[et_p2d_feelings.loc[:, "Parent Label"].str.contains(group), "Dwell time (fixation, ms)"]
    
    all_data[group] = {
        'center_x': float(center_x),
        'center_y': float(center_y),
        'color': df_feeling.loc[group, "Code_hex"],
        'detail_x': detail_x.tolist(),
        'detail_y': detail_y.tolist(),
        'detail_color': colors_shades,
        'marker_size': float(df_feeling.loc[group, "Choice"] * 10),
        'choice': float(df_feeling.loc[group, "Choice"])
    }

# Create overview figure
overview_fig = go.Figure()

for group, data in all_data.items():
    overview_fig.add_trace(go.Scatter(
        x=[data['center_x']], 
        y=[data['center_y']],
        mode='markers+text',
        marker=dict(
            size=data['marker_size'], 
            color=data['color'], 
            opacity=0.8, 
            line=dict(width=4, color='white')
        ),
        text=[group], 
        textposition="middle center",
        textfont=dict(color='white', size=16, family="Arial Black"),
        name=group,
        hovertemplate=f"<b>{group}</b><br>Choice: {data['choice']}<br><i>Click to explore!</i><extra></extra>"
    ))

overview_fig.update_layout(
    title="Click on any color to explore details!",
    xaxis_title="Respondent count (fixation dwells)",
    yaxis_title="Dwell time (fixation, ms)",
    height=600,
    showlegend=False,
    plot_bgcolor="#f8f9fa"
)

# Generate overview HTML
overview_html = pyo.plot(overview_fig, include_plotlyjs=True, output_type='div')

# Create the complete HTML with corrected JavaScript
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Feelings Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f8f9fa; 
        }}
        #back-btn {{ 
            display: none; 
            background: #2649B2; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            margin: 10px 0; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 16px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        #back-btn:hover {{ 
            background: #1a3a8a; 
            transform: translateY(-2px);
        }}
        .plot-container {{ 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ 
            color: #2649B2; 
            text-align: center; 
            margin-bottom: 20px;
        }}
        #main-plot {{
            width: 100%;
            height: 600px;
        }}
    </style>
</head>
<body>
    <h1>🎯 Interactive Feelings Analysis</h1>
    <button id="back-btn" onclick="showOverview()">⬅️ Back to Overview</button>
    
    <div class="plot-container">
        <div id="main-plot"></div>
    </div>
    
    <script>
        // Data for all groups
        const groupData = {json.dumps(all_data)};
        
        // Current state
        let currentView = 'overview';
        
        // Calculate back button position
        function getBackButtonPosition(groupName) {{
            const data = groupData[groupName];
            const minX = Math.min(...data.detail_x);
            const maxX = Math.max(...data.detail_x);
            const minY = Math.min(...data.detail_y);
            const maxY = Math.max(...data.detail_y);
            
            return {{
                x: maxX + (maxX - minX) * 0.3 + 1.0,
                y: maxY + (maxY - minY) * 0.2 + 0.5
            }};
        }}
        
        function showOverview() {{
            console.log('Showing overview');
            currentView = 'overview';
            document.getElementById('back-btn').style.display = 'none';
            
            // Create overview traces
            const traces = [];
            const groups = Object.keys(groupData);
            
            groups.forEach(group => {{
                const data = groupData[group];
                traces.push({{
                    x: [data.center_x],
                    y: [data.center_y],
                    mode: 'markers+text',
                    marker: {{
                        size: data.marker_size,
                        color: data.color,
                        opacity: 0.8,
                        line: {{ width: 4, color: 'white' }}
                    }},
                    text: [group],
                    textposition: 'middle center',
                    textfont: {{ color: 'white', size: 16, family: 'Arial Black' }},
                    name: group,
                    type: 'scatter',
                    hovertemplate: '<b>' + group + '</b><br>Choice: ' + data.choice + '<br><i>Click to explore!</i><extra></extra>'
                }});
            }});
            
            const layout = {{
                title: 'Click on any color to explore details!',
                xaxis: {{ title: 'Respondent count (fixation dwells)' }},
                yaxis: {{ title: 'Dwell time (fixation, ms)' }},
                height: 600,
                showlegend: false,
                plot_bgcolor: '##f8f9fa',  // 👈 ADD THIS LINE - controls the plot area background
                paper_bgcolor: '##ffffff'  // 👈 ADD THIS LINE - controls the entire figure background
            }};
            
            Plotly.newPlot('main-plot', traces, layout);
            
            // Add click event listener
            document.getElementById('main-plot').on('plotly_click', function(data) {{
                if (currentView === 'overview' && data.points && data.points.length > 0) {{
                    const groupName = data.points[0].data.name;
                    console.log('Clicked on group:', groupName);
                    showDetail(groupName);
                }}
            }});
        }}
        
        function showDetail(groupName) {{
            console.log('Showing detail for:', groupName);
            currentView = 'detail_' + groupName;
            document.getElementById('back-btn').style.display = 'block';
            
            const data = groupData[groupName];
            const backPos = getBackButtonPosition(groupName);
            
            // Create detail traces
            const traces = [
                {{
                    x: data.detail_x,
                    y: data.detail_y,
                    mode: 'markers',
                    marker: {{
                        size: 10,
                        color: data.color,
                        opacity: 0.7,
                        line: {{ width: 1, color: 'white' }}
                    }},
                    name: groupName + ' Details',
                    type: 'scatter',
                    hovertemplate: '<b>' + groupName + '</b><br>X: %{{x:.2f}}<br>Y: %{{y:.2f}}<extra></extra>'
                }},
                {{
                    x: [data.center_x],
                    y: [data.center_y],
                    mode: 'markers+text',
                    marker: {{
                        size: 25,
                        color: 'gold',
                        symbol: 'star',
                        line: {{ width: 3, color: data.color }}
                    }},
                    text: ['⭐ CENTER'],
                    textposition: 'top center',
                    textfont: {{ color: data.color, size: 12, family: 'Arial Black' }},
                    name: 'Center',
                    type: 'scatter'
                }},
                {{
                    x: [backPos.x],
                    y: [backPos.y],
                    mode: 'markers+text',
                    marker: {{
                        size: 40,
                        color: '#666666',
                        opacity: 0.9,
                        symbol: 'arrow-left'
                    }},
                    text: ['← Back'],
                    textposition: 'middle right',
                    textfont: {{ color: 'white', size: 14, family: 'Arial Black' }},
                    name: 'back_button',
                    type: 'scatter',
                    hovertemplate: '<b>Back to Overview</b><extra></extra>'
                }}
            ];
            
            const layout = {{
                title: groupName + ' Details (' + data.detail_x.length + ' points)',
                xaxis: {{ title: 'Detail X Coordinate' }},
                yaxis: {{ title: 'Detail Y Coordinate' }},
                height: 600,
                showlegend: false,
                plot_bgcolor: '##f8f9fa',  // 👈 ADD THIS LINE - controls the plot area background
                paper_bgcolor: '##ffffff'  // 👈 ADD THIS LINE - controls the entire figure background
            }};
            
            Plotly.newPlot('main-plot', traces, layout);
            
            // Add click event listener for back button
            document.getElementById('main-plot').on('plotly_click', function(data) {{
                if (data.points && data.points.length > 0) {{
                    if (data.points[0].data.name === 'back_button') {{
                        console.log('Back button clicked');
                        showOverview();
                    }}
                }}
            }});
        }}
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, initializing overview');
            showOverview();
        }});
    </script>
</body>
</html>
"""

# Save the HTML file
with open("feelings_interactive_click_in_progress.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Interactive HTML file created: feelings_interactive_click_in_progress.html")
print("🌐 This version has click-on-data interaction that works in HTML!")
print("💡 Click on any color circle to see details, then click the back button to return!")

# Also show in notebook if running there
overview_fig.show()