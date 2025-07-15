import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import numpy as np

# Same data generation as above...
np.random.seed(42)
colors = ['#2649B2', '#4A74F3', '#8E7DE3', '#9D5CE6']
groups = ['Group A', 'Group B', 'Group C', 'Group D']

group_data = {}
for i, group in enumerate(groups):
    center_x = (i % 2) * 4 + 2
    center_y = (i // 2) * 4 + 2
    
    n_points = np.random.randint(50, 100)
    detail_x = np.random.randn(n_points) * 1.2 + center_x
    detail_y = np.random.randn(n_points) * 1.2 + center_y
    
    group_data[group] = {
        'center': (center_x, center_y),
        'color': colors[i],
        'detail_x': detail_x,
        'detail_y': detail_y,
        'size': len(detail_x)
    }

def create_overview_plot():
    """Create overview with enhanced styling"""
    fig = go.Figure()
    
    for group, data in group_data.items():
        center_x, center_y = data['center']
        
        fig.add_trace(
            go.Scatter(
                x=[center_x], 
                y=[center_y],
                mode='markers+text',
                marker=dict(
                    size=60,
                    color=data['color'],
                    opacity=0.8,
                    line=dict(width=4, color='white')
                ),
                text=[group],
                textposition="middle center",
                textfont=dict(color='white', size=18, family="Arial Black"),
                name=group,
                hovertemplate=f"<b>{group}</b><br>" +
                            f"📊 {data['size']} data points<br>" +
                            "🖱️ <i>Click to explore!</i><extra></extra>",
                customdata=[group]
            )
        )
    
    fig.update_layout(
        title={
            'text': "🎯 Interactive Data Explorer - Click any group to dive deep!",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'color': '#2649B2'}
        },
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(248,249,250,0.8)',
        xaxis=dict(range=[-1, 7], gridcolor='rgba(38,73,178,0.1)'),
        yaxis=dict(range=[-1, 7], gridcolor='rgba(38,73,178,0.1)')
    )
    
    return fig

def create_detail_plot(selected_group):
    """Create enhanced detail plot"""
    fig = go.Figure()
    
    if selected_group and selected_group in group_data:
        data = group_data[selected_group]
        
        # Add scatter points with jitter for better visibility
        fig.add_trace(
            go.Scatter(
                x=data['detail_x'],
                y=data['detail_y'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=data['color'],
                    opacity=0.6,
                    line=dict(width=1, color='white')
                ),
                name=f'{selected_group} Data Points',
                hovertemplate=f"<b>{selected_group}</b><br>" +
                            "X: %{x:.2f}<br>" +
                            "Y: %{y:.2f}<extra></extra>"
            )
        )
        
        # Add center point
        center_x, center_y = data['center']
        fig.add_trace(
            go.Scatter(
                x=[center_x],
                y=[center_y],
                mode='markers+text',
                marker=dict(
                    size=30,
                    color='gold',
                    opacity=1.0,
                    line=dict(width=3, color=data['color']),
                    symbol='star'
                ),
                text=['⭐ CENTER'],
                textposition="top center",
                textfont=dict(color=data['color'], size=14, family="Arial Black"),
                name='Group Center'
            )
        )
        
        fig.update_layout(
            title={
                'text': f"🔍 {selected_group} Deep Dive ({data['size']} points)",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': data['color']}
            },
            xaxis_title="Detailed X Coordinate",
            yaxis_title="Detailed Y Coordinate",
            height=600,
            showlegend=False,
            plot_bgcolor='rgba(248,249,250,0.8)'
        )
    
    return fig

# Same app layout and callbacks as before...
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("🚀 Interactive Nested Scatter Plot", 
                style={'textAlign': 'center', 'color': '#2649B2', 'marginBottom': '10px'})
    ]),
    
    html.Div([
        html.Button(
            '⬅️ Back to Overview', 
            id='back-button',
            className='back-btn',
            style={
                'backgroundColor': '#2649B2',
                'color': 'white',
                'border': 'none',
                'padding': '12px 24px',
                'fontSize': '16px',
                'borderRadius': '25px',
                'cursor': 'pointer',
                'marginBottom': '15px',
                'display': 'none',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
                'transition': 'all 0.3s ease'
            }
        )
    ], style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Graph(
            id='main-graph',
            figure=create_overview_plot(),
            style={'height': '600px'}
        )
    ]),
    
    dcc.Store(id='current-view', data='overview'),
    dcc.Store(id='selected-group', data=None)
])

# Same callback as before...
@app.callback(
    [Output('main-graph', 'figure'),
     Output('current-view', 'data'),
     Output('selected-group', 'data'),
     Output('back-button', 'style')],
    [Input('main-graph', 'clickData'),
     Input('back-button', 'n_clicks')],
    [State('current-view', 'data'),
     State('selected-group', 'data')]
)
def update_plot(clickData, back_clicks, current_view, selected_group):
    ctx = dash.callback_context
    if not ctx.triggered:
        return (create_overview_plot(), 'overview', None, 
                {'backgroundColor': '#2649B2', 'color': 'white', 'border': 'none',
                 'padding': '12px 24px', 'fontSize': '16px', 'borderRadius': '25px',
                 'cursor': 'pointer', 'marginBottom': '15px', 'display': 'none',
                 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'})
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'back-button' and back_clicks:
        return (create_overview_plot(), 'overview', None,
                {'backgroundColor': '#2649B2', 'color': 'white', 'border': 'none',
                 'padding': '12px 24px', 'fontSize': '16px', 'borderRadius': '25px',
                 'cursor': 'pointer', 'marginBottom': '15px', 'display': 'none',
                 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'})
    
    elif trigger_id == 'main-graph' and clickData and current_view == 'overview':
        if 'points' in clickData and len(clickData['points']) > 0:
            clicked_group = clickData['points'][0]['customdata']
            
            return (create_detail_plot(clicked_group), 'detail', clicked_group,
                    {'backgroundColor': '#2649B2', 'color': 'white', 'border': 'none',
                     'padding': '12px 24px', 'fontSize': '16px', 'borderRadius': '25px',
                     'cursor': 'pointer', 'marginBottom': '15px', 'display': 'block',
                     'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'})
    
    return (dash.no_update, dash.no_update, dash.no_update, dash.no_update)

if __name__ == '__main__':
    app.run(debug=True)