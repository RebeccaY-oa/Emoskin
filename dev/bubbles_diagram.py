import plotly.graph_objects as go
import plotly.offline as pyo
import numpy as np
import pandas as pd
import pathlib
import json
from itertools import product
import re
import sys

class PreprocessedFlexibleFeelingsAnalyzer:
    def __init__(self):
        # Data loading
        parent_path = pathlib.Path(__file__).parent.parent
        self.df = pd.read_excel(parent_path / "Results" / "Tableaux" / "Feelings" / "Feelings.xlsx", index_col=[0, 1])
        self.et = pd.read_excel(parent_path / "Files" / "ET_modified.xlsx", usecols="B:C, F:L, P:AO, AQ:AW, BC: BE", skiprows=6)
        self.hex = pd.read_excel(parent_path / "Files" / "code_hex.xlsx", sheet_name="Données Complètes palettes", index_col="Nom Teinte")
        self.survey = pd.read_excel(parent_path / "Files" / "survey.xlsx", sheet_name="Full Survey Response", index_col="OA Name")
        
        # Filter ET data
        self.et_p2d = self.et.loc[self.et.loc[:, "Parent Label"].str.contains("P2d", na=False), :]
        
        # Constants
        self.feelings = list(self.df.index.get_level_values(0).unique())
        self.colors = ["Reds", "Greens", "Oranges", "Yellows", "Whites", "Lavenders", "Blues"]
        self.codes_hex = ["#EDCCD5", "#C3E9CB", "#F7D0B7", "#FFEEC4", "#F9F9FA", "#D9C8E5", "#C0E3F6"]
        
        # Get available metrics from the data
        self.available_metrics = self.get_available_metrics()
        
        # Store base data for processing
        self.base_feelings_data = {}
        self.process_base_data()
        
        # 🚀 Pre-process ALL metric combinations
        self.all_combinations_data = {}
        self.preprocess_all_combinations()
    

    def get_available_metrics(self):
        """Get list of available numeric metrics from the dataframe"""
        sample_feeling = self.feelings[0]
        df_sample = self.df.loc[sample_feeling, :]
        numeric_columns = df_sample.select_dtypes(include=[np.number]).columns.tolist()
        
        excluded_patterns = ['index', 'level', 'unnamed', 'choice', '%']
        
        metrics = [col for col in numeric_columns 
                if not any(pattern.lower() in col.lower() for pattern in excluded_patterns)
                and not re.search(r'\bratio\b', col.lower())]  # ✅ Add this line
        
        print("📊 Available metrics for both X and Y axes:")
        for metric in metrics:
            print(f"  - {metric}")
        
        return metrics
    
    def process_base_data(self):
        """Process base data (without specific metrics) for all feelings"""
        print(f"🔄 Processing base data for {len(self.feelings)} feelings...")
        
        for feeling in self.feelings:
            try:
                df_feeling = self.df.loc[feeling, :]
                et_p2d_feelings = self.et_p2d.loc[self.et_p2d.loc[:, "Parent Label"].str.contains(feeling), :]
                et_p2d_feelings.loc[:, "Label_modified"] = et_p2d_feelings["Label_modified"].str.split("_").str[-1]
                et_p2d_feelings = et_p2d_feelings.set_index("Label_modified")
                choice = self.survey.loc[self.survey["Word_EmotionOrBenefit"] == feeling, :]
                
                # Add hex codes to color families
                for i, color in enumerate(self.colors):
                    if color in df_feeling.index:
                        df_feeling.loc[color, "Code_hex"] = self.codes_hex[i]
                
                self.base_feelings_data[feeling] = {
                    'df_feeling': df_feeling,
                    'et_p2d_feelings': et_p2d_feelings,
                    'choice': choice
                }
                print(f"✅ Processed base data for: {feeling}")
            except Exception as e:
                print(f"❌ Error processing {feeling}: {e}")
    
    def process_feeling_with_metrics(self, feeling, x_metric, y_metric):
        """Process data for a specific feeling with specified X and Y metrics"""
        if feeling not in self.base_feelings_data:
            return None, 0
        
        try:
            base_data = self.base_feelings_data[feeling]
            df_feeling = base_data['df_feeling']
            et_p2d_feelings = base_data['et_p2d_feelings']
            choice = base_data['choice']
            
            groups = df_feeling.index
            all_data = {}
            max_clicks_found = 0
            
            for group in groups:
                try:
                    # ✅ Use the ACTUAL selected metrics
                    center_x = df_feeling.loc[group, x_metric]
                    center_y = df_feeling.loc[group, y_metric]
                    
                    # Skip if values are NaN
                    if pd.isna(center_x) or pd.isna(center_y):
                        continue
                        
                except (KeyError, IndexError):
                    print(f"⚠️ Metric not found for {group}: {x_metric} or {y_metric}")
                    continue
                
                group_data = et_p2d_feelings.loc[et_p2d_feelings.loc[:, "Parent Label"].str.contains(group), :]
                
                # For detail view, get actual metric values
                if x_metric in et_p2d_feelings.columns:
                    detail_x = et_p2d_feelings.loc[et_p2d_feelings.loc[:, "Parent Label"].str.contains(group), x_metric]
                    detail_x = detail_x.dropna()  # Remove NaN values
                else:
                    detail_x = pd.Series([center_x] * len(group_data), index=group_data.index)
                
                if y_metric in et_p2d_feelings.columns:
                    detail_y = et_p2d_feelings.loc[et_p2d_feelings.loc[:, "Parent Label"].str.contains(group), y_metric]
                    detail_y = detail_y.dropna()  # Remove NaN values
                else:
                    detail_y = pd.Series([center_y] * len(group_data), index=group_data.index)
                
                # Align detail_x and detail_y indices
                common_indices = detail_x.index.intersection(detail_y.index)
                detail_x = detail_x.loc[common_indices]
                detail_y = detail_y.loc[common_indices]
                
                if len(detail_x) == 0:  # Skip if no valid data
                    continue
                
                # Process clicks and colors
                choice_group = choice[choice.index.isin(common_indices)]
                choice_group = choice_group.index.value_counts()
                tot_choice = int(choice_group.sum()) if not choice_group.empty else 0
                
                hex_group = self.hex[self.hex.index.isin(common_indices)]
                hex_group = hex_group.reindex(common_indices)
                choice_group = choice_group.reindex(common_indices)
                
                if not choice_group.empty:
                    max_clicks_in_group = choice_group.max() if choice_group.notna().any() else 0
                    max_clicks_found = max(max_clicks_found, max_clicks_in_group)
                
                choice_group[choice_group.isna()] = 0
                detail_choice = choice_group.tolist()
                choice_group = choice_group + 1
                detail_size = (choice_group*10).tolist()
                
                group_colors_shades = hex_group["HEX"].fillna("#CCCCCC").tolist()  # Default color for missing
                detail_names = common_indices.tolist()
                
                all_data[group] = {
                    'center_x': float(center_x),
                    'center_y': float(center_y),
                    'color': df_feeling.loc[group, "Code_hex"],
                    'detail_x': detail_x.tolist(),
                    'detail_y': detail_y.tolist(),
                    'detail_color': group_colors_shades,
                    'detail_size': detail_size,
                    'detail_choice': detail_choice,
                    'detail_names': detail_names,
                    'marker_size': int(tot_choice * 10) if tot_choice > 0 else 10,
                    'choice': tot_choice
                }
            
            return all_data, max_clicks_found
            
        except Exception as e:
            print(f"❌ Error processing {feeling} with {x_metric} vs {y_metric}: {e}")
            return {}, 0
    
    def preprocess_all_combinations(self):
        """🚀 Pre-process ALL possible combinations of feelings and metrics"""
        total_combinations = len(self.feelings) * len(self.available_metrics) * len(self.available_metrics)
        print(f"\n🚀 Pre-processing {total_combinations:,} metric combinations...")
        print(f"   📊 {len(self.feelings)} feelings")
        print(f"   ↔️ {len(self.available_metrics)} X-axis metrics") 
        print(f"   ↕️ {len(self.available_metrics)} Y-axis metrics")
        print(f"   ⏱️ This may take a few minutes...")
        
        processed_count = 0
        
        for feeling in self.feelings:
            self.all_combinations_data[feeling] = {}
            
            for x_metric in self.available_metrics:
                self.all_combinations_data[feeling][x_metric] = {}
                
                for y_metric in self.available_metrics:
                    try:
                        data, max_clicks = self.process_feeling_with_metrics(feeling, x_metric, y_metric)
                        self.all_combinations_data[feeling][x_metric][y_metric] = {
                            'data': data,
                            'max_clicks': max_clicks
                        }
                        processed_count += 1
                        
                        # Progress indicator
                        if processed_count % 50 == 0:
                            progress = (processed_count / total_combinations) * 100
                            print(f"   ⏳ Progress: {processed_count:,}/{total_combinations:,} ({progress:.1f}%)")
                            
                    except Exception as e:
                        print(f"❌ Error processing {feeling} - {x_metric} vs {y_metric}: {e}")
                        self.all_combinations_data[feeling][x_metric][y_metric] = {
                            'data': {},
                            'max_clicks': 0
                        }
        
        print(f"✅ Successfully pre-processed {processed_count:,} combinations!")
        print(f"💾 Memory usage: ~{self.estimate_memory_usage()} MB")
    
    def estimate_memory_usage(self):
        """Estimate memory usage of all combinations data"""
        size = sys.getsizeof(self.all_combinations_data)
        return round(size / (1024 * 1024), 2)
    
    def generate_html(self):
        """Generate the complete interactive HTML with all pre-processed combinations"""
        available_feelings = list(self.base_feelings_data.keys())
        
        # Create dropdown options
        feeling_options = ""
        for i, feeling in enumerate(available_feelings):
            selected = "selected" if i == 0 else ""
            feeling_options += f'<option value="{feeling}" {selected}>{feeling}</option>\n'
        
        metric_options = ""
        for metric in self.available_metrics:
            metric_options += f'<option value="{metric}">{metric}</option>\n'
        
        default_x = "Respondent count (fixation dwells)"
        default_y = "Dwell time (fixation, ms)"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Eye Tracking Data Visualition</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #ffffff; 
        }}
        
        .controls-section {{
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            gap: 20px;
            flex-wrap: wrap;
            align-items: flex-end;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .dropdown-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        
        .dropdown-label {{
            font-weight: bold;
            color: #2649B2;
            font-size: 14px;
            text-align: center;
        }}
        
        .dropdown-select {{
            padding: 10px 14px;
            border: 2px solid #2649B2;
            border-radius: 8px;
            background-color: white;
            color: #2649B2;
            font-size: 14px;
            cursor: pointer;
            outline: none;
            min-width: 220px;
            height: 44px;
            transition: all 0.3s ease;
        }}
        
        .dropdown-select:hover {{
            background-color: #f0f4ff;
            border-color: #1a3a8a;
        }}
        
        .update-btn {{
            background: linear-gradient(135deg, #2649B2, #1a3a8a);
            color: white;
            border: none;
            padding: 0 28px;
            height: 44px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(38, 73, 178, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 22px;
        }}
        
        .update-btn:hover {{
            background: linear-gradient(135deg, #1a3a8a, #0f2557);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(38, 73, 178, 0.4);
        }}
        
        //.info-bar {{
        //    background: linear-gradient(135deg, #e8f4fd, #d4edda);
        //    padding: 10px 20px;
        //    border-radius: 8px;
        //    margin-bottom: 20px;
        //    text-align: center;
        //    color: #155724;
        //    border: 1px solid #c3e6cb;
        //}}
        
        .main-container {{
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }}
        
        .plot-section {{
            flex: 1;
        }}
        
        .sidebar {{
            width: 200px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        #back-btn {{ 
            display: none; 
            background: #2649B2; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 16px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            width: 100%;
        }}
        
        #back-btn:hover {{ 
            background: #1a3a8a; 
            transform: translateY(-2px);
        }}
        
        .legend-container {{
            display: none;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .legend-title {{
            font-weight: bold;
            color: #2649B2;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-size: 12px;
            color: #333;
        }}
        
        .legend-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #999999;
            border: 1px solid #666666;
            margin-right: 8px;
            flex-shrink: 0;
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
        
        .loading {{
            text-align: center;
            color: #2649B2;
            font-style: italic;
            margin: 20px 0;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <h1>👁️‍🗨️ Eye Tracking Data Visualisation</h1>
    
    <!-- <div class="info-bar">
        ✅ <strong>{len(available_feelings) * len(self.available_metrics) * len(self.available_metrics):,} combinations pre-processed</strong> - All metric changes use real data!
    </div> -->
    
    <div class="controls-section">
        <div class="dropdown-container">
            <label class="dropdown-label" for="feeling-select">📊 Feeling Or Functional Benefit</label>
            <select id="feeling-select" class="dropdown-select">
                {feeling_options}
            </select>
        </div>
        
        <div class="dropdown-container">
            <label class="dropdown-label" for="x-metric-select">↔️ X-Axis Metric</label>
            <select id="x-metric-select" class="dropdown-select">
                {metric_options.replace(f'<option value="{default_x}">', f'<option value="{default_x}" selected>')}
            </select>
        </div>
        
        <div class="dropdown-container">
            <label class="dropdown-label" for="y-metric-select">↕️ Y-Axis Metric</label>
            <select id="y-metric-select" class="dropdown-select">
                {metric_options.replace(f'<option value="{default_y}">', f'<option value="{default_y}" selected>')}
            </select>
        </div>
        
        <button class="update-btn" onclick="updateVisualization()">🚀 Update Plot</button>
    </div>
    
    <div id="loading-message" class="loading" style="display: none;">
        🔄 Switching to new metric combination...
    </div>
    
    <div class="main-container">
        <div class="plot-section">
            <div class="plot-container">
                <div id="main-plot"></div>
            </div>
        </div>
        
        <div class="sidebar">
            <button id="back-btn" onclick="showOverview()">⬅️ Back to Overview</button>
            
            <div id="legend-container" class="legend-container">
                <div class="legend-title">Circle Size = Clicks</div>
                <div class="legend-item">
                    <div class="legend-circle" style="width: 10px; height: 10px;"></div>
                    <span>0 clicks</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="width: 20px; height: 20px;"></div>
                    <span>1 click</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="width: 30px; height: 30px;"></div>
                    <span>2 clicks</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="width: 40px; height: 40px;"></div>
                    <span>3 clicks</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="width: 60px; height: 60px;"></div>
                    <span>5+ clicks</span> <!-- A CHANGER POUR METTRE TOUTES LES TAILLES DE RONDS -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // ✅ ALL PRE-PROCESSED COMBINATIONS DATA
        const allCombinationsData = {json.dumps(self.all_combinations_data)};
        const availableFeelings = {json.dumps(available_feelings)};
        const availableMetrics = {json.dumps(self.available_metrics)};
        
        // Current state
        let currentView = 'overview';
        let currentFeeling = availableFeelings[0];
        let currentXMetric = "{default_x}";
        let currentYMetric = "{default_y}";
        
        console.log('📊 Loaded data for', Object.keys(allCombinationsData).length, 'feelings');
        console.log('🔍 First feeling has', Object.keys(allCombinationsData[currentFeeling] || {{}}).length, 'X-axis metrics');
        
        function updateVisualization() {{
            const selectedFeeling = document.getElementById('feeling-select').value;
            const selectedXMetric = document.getElementById('x-metric-select').value;
            const selectedYMetric = document.getElementById('y-metric-select').value;
            
            console.log('🔄 Updating to:', selectedFeeling, selectedXMetric, 'vs', selectedYMetric);
            
            // Show loading message
            document.getElementById('loading-message').style.display = 'block';
            
            // Update current state
            currentFeeling = selectedFeeling;
            currentXMetric = selectedXMetric;
            currentYMetric = selectedYMetric;
            
            // Simulate brief loading for UX
            setTimeout(() => {{
                document.getElementById('loading-message').style.display = 'none';
                showOverview();
            }}, 200);
        }}
        
        function getCurrentData() {{
            // ✅ Get the ACTUAL pre-processed data for current combination
            try {{
                const data = allCombinationsData[currentFeeling][currentXMetric][currentYMetric];
                console.log('📊 Retrieved data for', currentFeeling, currentXMetric, currentYMetric, ':', Object.keys(data.data).length, 'groups');
                return data;
            }} catch (error) {{
                console.error('❌ Error getting data for combination:', currentFeeling, currentXMetric, currentYMetric, error);
                return {{ data: {{}}, max_clicks: 0 }};
            }}
        }}
        
        function showOverview() {{
            console.log('📈 Showing overview for:', currentFeeling, 'X:', currentXMetric, 'Y:', currentYMetric);
            currentView = 'overview';
            document.getElementById('back-btn').style.display = 'none';
            document.getElementById('legend-container').style.display = 'none';
            
            // ✅ Get REAL data for current metric combination
            const currentData = getCurrentData();
            const groupData = currentData.data || {{}};
            
            // Create overview traces with REAL data
            const traces = [];
            const groups = Object.keys(groupData);
            
            if (groups.length === 0) {{
                // Show message if no data available
                const layout = {{
                    title: currentYMetric + ' vs ' + currentXMetric + ' for ' + currentFeeling,
                    xaxis: {{ title: currentXMetric }},
                    yaxis: {{ title: currentYMetric }},
                    height: 600,
                    showlegend: false,
                    plot_bgcolor: '#DBDBDB',
                    paper_bgcolor: '#ffffff',
                    annotations: [{{
                        text: 'No data available for this metric combination',
                        x: 0.5, y: 0.5, xref: 'paper', yref: 'paper',
                        showarrow: false, font: {{ size: 16, color: '#666' }}
                    }}]
                }};
                Plotly.newPlot('main-plot', [], layout);
                return;
            }}
            
            groups.forEach(group => {{
                const data = groupData[group];
                traces.push({{
                    x: [data.center_x],
                    y: [data.center_y],
                    mode: 'markers+text',
                    marker: {{
                        size: data.marker_size,
                        color: data.color,
                        opacity: 1,
                        line: {{ width: 4, color: '#DBDBDB' }}
                    }},
                    text: data.choice,
                    textposition: 'middle center',
                    textfont: {{ color: '#808080', size: 16, family: 'Arial Black' }},
                    name: group,
                    type: 'scatter',
                    hovertemplate: '<b>' + group + '</b><br>Choice: ' + data.choice + '<br><i>Click to explore!</i><extra></extra>'
                }});
            }});
            
            const layout = {{
                title: currentYMetric + ' vs ' + currentXMetric + ' for ' + currentFeeling,
                xaxis: {{ 
                    title: currentXMetric,
                    showgrid: true,
                    gridwidth: 2,
                    gridcolor: '#e0e0e0',
                    zeroline: true,
                    zerolinecolor: '#d0d0d0',
                    zerolinewidth: 2
                }},
                yaxis: {{ 
                    title: currentYMetric,
                    showgrid: true,
                    gridwidth: 2,
                    gridcolor: '#e0e0e0',
                    zeroline: true,
                    zerolinecolor: '#d0d0d0',
                    zerolinewidth: 2
                }},
                height: 600,
                showlegend: false,
                plot_bgcolor: '#DBDBDB',
                paper_bgcolor: '#ffffff'
            }};
            
            Plotly.newPlot('main-plot', traces, layout);
            
            // Add click event listener
            document.getElementById('main-plot').on('plotly_click', function(data) {{
                if (currentView === 'overview' && data.points && data.points.length > 0) {{
                    const groupName = data.points[0].data.name;
                    console.log('👆 Clicked on group:', groupName);
                    showDetail(groupName);
                }}
            }});
        }}
        
        function showDetail(groupName) {{
            console.log('🔍 Showing detail for:', groupName, 'in feeling:', currentFeeling);
            currentView = 'detail_' + groupName;
            document.getElementById('back-btn').style.display = 'block';
            document.getElementById('legend-container').style.display = 'block';
            
            // ✅ Get REAL data for current metric combination
            const currentData = getCurrentData();
            const groupData = currentData.data || {{}};
            const data = groupData[groupName];
            
            if (!data) {{
                console.error('❌ No data found for group:', groupName);
                return;
            }}
            
            // Create rich customdata with multiple values
            const customDataArray = data.detail_x.map((x, i) => [
                data.detail_choice[i] || 0,           // Index 0: Clicks
                data.detail_names ? data.detail_names[i] : `Point ${{i+1}}`,  // Index 1: Color name
                data.detail_x[i],                     // Index 2: X value
                data.detail_y[i]                     // Index 3: Y value
            ]);
            
            // Create detail traces with REAL data
            const traces = [
                {{
                    x: data.detail_x,
                    y: data.detail_y,
                    customdata: customDataArray,
                    mode: 'markers+text',
                    // mode: 'markers',
                    // text: customdata[1],
                    texttemplate: '%{{customdata[1]}}',
                    textposition: 'bottom center',
                    textfont: {{ color: '#808080', size: 10, family: 'Arial Black' }},
                    marker: {{
                        size: data.detail_size,
                        color: data.detail_color,
                        opacity: 1,
                        line: {{ width: 1, color: '#DBDBDB' }}
                    }},
                    name: groupName + ' Details',
                    type: 'scatter',
                    hovertemplate: '<b>🎨 %{{customdata[1]}}</b><br>' +
                                  '<b>📊 ' + groupName + '</b><br>' +
                                  '▪️ ' + currentXMetric + ': %{{x:.2f}}<br>' +
                                  '▪️ ' + currentYMetric + ': %{{y:.2f}}<br>' +
                                  '🖱️ Clicks: %{{customdata[0]}}<br>' 
                }}
            ];
            
            const layout = {{
                title: groupName + ' Details (' + data.detail_x.length + ' points) - ' + currentFeeling,
                xaxis: {{ 
                    title: currentXMetric,
                    showgrid: true,
                    gridwidth: 2,
                    gridcolor: '#e0e0e0',
                    zeroline: true,
                    zerolinecolor: '#d0d0d0',
                    zerolinewidth: 2
                }},
                yaxis: {{ 
                    title: currentYMetric,
                    showgrid: true,
                    gridwidth: 2,
                    gridcolor: '#e0e0e0',
                    zeroline: true,
                    zerolinecolor: '#d0d0d0',
                    zerolinewidth: 2
                }},
                height: 600,
                showlegend: false,
                plot_bgcolor: '#DBDBDB',
                paper_bgcolor: '#ffffff'
            }};
            
            Plotly.newPlot('main-plot', traces, layout);
        }}
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🚀 DOM loaded, initializing with real pre-processed data');
            showOverview();
        }});
    </script>
</body>
</html>
        """
        
        return html_content

# Create analyzer instance and generate HTML
print("🚀 Initializing Fully Pre-processed Feelings Analyzer...")
analyzer = PreprocessedFlexibleFeelingsAnalyzer()

# Generate and save HTML
html_content = analyzer.generate_html()

with open("eye_tracking_data_viz.html", "w", encoding="utf-8") as f:
    f.write(html_content)

total_combinations = len(analyzer.all_combinations_data) * len(analyzer.available_metrics) * len(analyzer.available_metrics)

print(f"\n🎉 SUCCESS! Created: eye_tracking_data_viz.html")
print(f"✅ Features:")
print(f"   📊 ALL {len(analyzer.base_feelings_data)} feelings available")
print(f"   ↔️ {len(analyzer.available_metrics)} X-axis metrics")
print(f"   ↕️ {len(analyzer.available_metrics)} Y-axis metrics") 
print(f"   🚀 {total_combinations:,} combinations pre-processed")
print(f"   ⚡ INSTANT metric switching with REAL data!")
print(f"   💾 Estimated memory usage: ~{analyzer.estimate_memory_usage()} MB")
print(f"\n💡 Now when you change metrics, you'll see ACTUAL data changes!")