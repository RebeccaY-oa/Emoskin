import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def hex_to_rgba(hex_color, alpha=0.6):
    """Convert hex color to rgba with transparency"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{alpha})'
    return hex_color

class ColorEmotionVisualizer:
    def __init__(self, file_path):
        """Initialize the visualizer with data from CSV or XLSX file"""
        
        # Determine file type and load accordingly
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            print("📊 Loading XLSX file...")
            self.df = pd.read_excel(file_path)
        else:
            print("📊 Loading CSV file...")
            self.df = pd.read_csv(file_path)
        
        # Clean column names
        self.df.columns = self.df.columns.str.strip()
        
        # Fix the Feeling column - forward fill empty cells (handles merged cells from Excel)
        self.df['Feeling'] = self.df['Feeling'].fillna(method='ffill') # type: ignore
        
        # Remove any rows where Feeling is still NaN
        self.df = self.df.dropna(subset=['Feeling'])
        
        # Clean any leading/trailing whitespace
        self.df['Feeling'] = self.df['Feeling'].str.strip()
        self.df['Colour'] = self.df['Colour'].str.strip()
        
        # Remove any completely empty rows
        self.df = self.df.dropna(how='all')
        
        self.original_df = self.df.copy()
        
        # Define color palette
        self.color_palette = {
            'Happy': '#2649B2',
            'Relaxed': '#4A74F3', 
            'Energized': '#8E7DE3',
            'Blues': '#C0E3F6',
            'Greens': '#C3E9CB',
            'Lavenders': '#D9C8E5',
            'Oranges': '#F7D0B7',
            'Reds': '#EDCCD5',
            'Whites': '#F9F9FA',
            'Yellows': '#FFEEC4'
        }
        
        # Get numeric columns for sizing (excluding non-numeric columns)
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        # Remove 'Choice' if it exists as it's likely categorical
        if 'Choice' in numeric_cols:
            numeric_cols.remove('Choice')
            
        self.numeric_columns = numeric_cols
        
        # Create output directory for saved plots
        self.output_dir = "html_viz"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"✅ Data preprocessing complete!")
        print(f"📋 Total records: {len(self.df)}")
        print(f"🎭 Unique emotions: {list(self.df['Feeling'].unique())}")
        print(f"🎨 Unique colors: {list(self.df['Colour'].unique())}")
        print(f"📊 Numeric columns available: {self.numeric_columns}")
        
        # Show emotion breakdown
        emotion_counts = self.df['Feeling'].value_counts()
        print(f"\n📈 Records per emotion:")
        for emotion, count in emotion_counts.items():
            print(f"   {emotion}: {count} colors")
        
    def create_sankey_chart(self, size_metric):
        """Create Sankey diagram"""
        filtered_df = self.df.copy()
        
        # Prepare data for Sankey
        feelings = sorted(filtered_df['Feeling'].unique())
        colors = sorted(filtered_df['Colour'].unique())
        
        # Create node labels and colors
        node_labels = list(feelings) + list(colors)
        node_colors = [self.color_palette.get(label, '#cccccc') for label in node_labels]
        
        # Create links
        source = []
        target = []
        values = []
        link_colors = []
        
        feeling_to_idx = {feeling: i for i, feeling in enumerate(feelings)}
        color_to_idx = {color: i + len(feelings) for i, color in enumerate(colors)}
        
        for _, row in filtered_df.iterrows():
            feeling_idx = feeling_to_idx[row['Feeling']]
            color_idx = color_to_idx[row['Colour']]
            value = float(row[size_metric])  # type: ignore # Ensure it's a number
            
            source.append(feeling_idx)
            target.append(color_idx)
            values.append(value)
            # Convert hex to rgba for transparency
            base_color = self.color_palette.get(row['Feeling'], '#cccccc')
            transparent_color = hex_to_rgba(base_color, 0.6)
            link_colors.append(transparent_color)
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color=node_colors
            ),
            link=dict(
                source=source,
                target=target,
                value=values,
                color=link_colors
            )
        )])
        
        fig.update_layout(
            title=f"Sankey Diagram: Emotion to Color Flow<br>Sized by {size_metric}",
            font_size=12,
            height=600,
            width=1000
        )
        
        return fig
    
    def create_icicle_chart(self, size_metric):
        """Create Icicle chart"""
        filtered_df = self.df.copy()
        
        # Prepare data for Icicle
        icicle_data = []
        
        # Add parent nodes (feelings)
        for feeling in sorted(filtered_df['Feeling'].unique()):
            icicle_data.append({
                'ids': feeling,
                'labels': feeling,
                'parents': '',
                'values': float(filtered_df[filtered_df['Feeling'] == feeling][size_metric].sum())
            })
        
        # Add child nodes (colors)
        for _, row in filtered_df.iterrows():
            icicle_data.append({
                'ids': f"{row['Feeling']}_{row['Colour']}",
                'labels': row['Colour'],
                'parents': row['Feeling'],
                'values': float(row[size_metric]) # type: ignore
            })
        
        icicle_df = pd.DataFrame(icicle_data)
        
        fig = go.Figure(go.Icicle(
            ids=icicle_df['ids'],
            labels=icicle_df['labels'],
            parents=icicle_df['parents'],
            values=icicle_df['values'],
            branchvalues="total",
            maxdepth=2,
            tiling=dict(orientation='v')
        ))
        
        fig.update_layout(
            title=f"Icicle Chart: Hierarchical Color Preferences<br>Sized by {size_metric}",
            font_size=12,
            height=600,
            width=1000
        )
        
        return fig
    
    def create_combined_chart(self, size_metric):
        """Create both charts side by side"""
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Sankey Diagram', 'Icicle Chart'),
            specs=[[{'type': 'sankey'}, {'type': 'icicle'}]],
            horizontal_spacing=0.05
        )
        
        # Add Sankey
        sankey_fig = self.create_sankey_chart(size_metric)
        sankey_trace = sankey_fig.data[0]
        fig.add_trace(sankey_trace, row=1, col=1)
        
        # Add Icicle
        icicle_fig = self.create_icicle_chart(size_metric)
        icicle_trace = icicle_fig.data[0]
        fig.add_trace(icicle_trace, row=1, col=2)
        
        fig.update_layout(
            title=f"Combined View: Sized by {size_metric}",
            height=600,
            width=1400
        )
        
        return fig
    
    def save_all_charts_for_all_metrics(self):
        """Save all chart types for all available metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        print(f"🚀 Starting to generate charts...")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Available metrics: {len(self.numeric_columns)}")
        print(f"🎨 Chart types: Sankey, Icicle, Combined")
        print("-" * 50)
        
        for i, metric in enumerate(self.numeric_columns, 1):
            print(f"📈 Processing metric {i}/{len(self.numeric_columns)}: {metric}")
            
            # Create safe filename
            safe_metric = metric.replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'pct').replace(',', '')
            
            try:
                # Create and save Sankey chart
                sankey_fig = self.create_sankey_chart(metric)
                sankey_filename = f"sankey_{safe_metric}_{timestamp}.html"
                sankey_filepath = os.path.join(self.output_dir, sankey_filename)
                sankey_fig.write_html(sankey_filepath, include_plotlyjs=True)
                saved_files.append(sankey_filepath)
                print(f"   ✅ Sankey saved: {sankey_filename}")
                
                # Create and save Icicle chart
                icicle_fig = self.create_icicle_chart(metric)
                icicle_filename = f"icicle_{safe_metric}_{timestamp}.html"
                icicle_filepath = os.path.join(self.output_dir, icicle_filename)
                icicle_fig.write_html(icicle_filepath, include_plotlyjs=True)
                saved_files.append(icicle_filepath)
                print(f"   ✅ Icicle saved: {icicle_filename}")
                
                # Create and save Combined chart
                combined_fig = self.create_combined_chart(metric)
                combined_filename = f"combined_{safe_metric}_{timestamp}.html"
                combined_filepath = os.path.join(self.output_dir, combined_filename)
                combined_fig.write_html(combined_filepath, include_plotlyjs=True)
                saved_files.append(combined_filepath)
                print(f"   ✅ Combined saved: {combined_filename}")
                
            except Exception as e:
                print(f"   ❌ Error with metric '{metric}': {str(e)}")
        
        print("-" * 50)
        print(f"🎉 Generation complete!")
        print(f"📄 Total files saved: {len(saved_files)}")
        print(f"📁 Location: {os.path.abspath(self.output_dir)}")
        
        return saved_files
    
    def save_default_charts(self):
        """Save charts with default metric"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Try to use the first numeric column as default
        if self.numeric_columns:
            default_metric = self.numeric_columns[0]
        else:
            print("❌ No numeric columns found for visualization!")
            return []
        
        print(f"🚀 Generating default charts with metric: {default_metric}")
        print(f"📁 Output directory: {self.output_dir}")
        print("-" * 50)
        
        try:
            charts = {
                'sankey': self.create_sankey_chart(default_metric),
                'icicle': self.create_icicle_chart(default_metric),
                'combined': self.create_combined_chart(default_metric)
            }
            
            saved_files = []
            for chart_type, fig in charts.items():
                filename = f"{chart_type}_default_{timestamp}.html"
                filepath = os.path.join(self.output_dir, filename)
                fig.write_html(filepath, include_plotlyjs=True)
                saved_files.append(filepath)
                print(f"✅ {chart_type.capitalize()} chart saved: {filename}")
            
            print("-" * 50)
            print(f"🎉 Default charts saved successfully!")
            print(f"📄 Total files: {len(saved_files)}")
            print(f"📁 Location: {os.path.abspath(self.output_dir)}")
            
            return saved_files
            
        except Exception as e:
            print(f"❌ Error creating charts: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

def main():
    """Main function to run the script"""
    
    # Look for both CSV and XLSX files
    possible_files = [
        "/home/user/Emoskin/Results/Tableaux/Feelings/Feelings.xlsx",
    ]
    
    file_path = None
    for path in possible_files:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        print("❌ Could not find data file. Looking for:")
        for path in possible_files:
            print(f"   {path}")
        return
    
    print("=" * 60)
    print("🎨 COLOR EMOTION VISUALIZER")
    print("=" * 60)
    print(f"📁 Using file: {file_path}")
    
    try:
        # Initialize the visualizer
        visualizer = ColorEmotionVisualizer(file_path)
        
        # Ask user what they want to generate
        print("\nChoose what to generate:")
        print("1. Default charts (3 charts with first available metric)")
        print(f"2. All charts for all metrics ({len(visualizer.numeric_columns) * 3} charts total)")
        
        choice = input("\nEnter your choice (1 or 2) [default: 1]: ").strip()
        
        if choice == "2":
            # Generate all charts for all metrics
            saved_files = visualizer.save_all_charts_for_all_metrics()
        else:
            # Generate default charts
            saved_files = visualizer.save_default_charts()
        
        if saved_files:
            print(f"\n🎯 All files saved in: {os.path.abspath(visualizer.output_dir)}")
            print("🌐 Open any HTML file in your web browser to view the interactive charts!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()