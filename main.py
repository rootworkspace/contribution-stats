import json
from datetime import datetime, timedelta

def get_color(count):
    """Maps commit counts to a semi-transparent color palette."""
    # rgba(Red, Green, Blue, Alpha)
    colors = [
        "rgba(130, 130, 130, 0.15)", # 0
        "rgba(255, 105, 180, 0.5)",  # 1-2
        "rgba(190, 80, 255, 0.65)",  # 3-5
        "rgba(90, 130, 255, 0.8)",   # 6-15
        "rgba(0, 220, 255, 0.9)"     # 16+
    ]
    if count == 0: return colors[0]
    if count <= 2: return colors[1]
    if count <= 5: return colors[2]
    if count <= 15: return colors[3]
    return colors[4]

def generate_svg_graph(json_path, output_path="contribution_graph.svg"):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    daily_commits = sorted(data["daily_commits"].items())
    
    # Layout Constants
    cell_size, padding = 11, 2
    margin_left, margin_top = 30, 25
    legend_height = 25
    text_style = 'fill: rgba(128, 130, 140, 0.8); font-family: sans-serif; font-size: 9px;'
    
    # Process data into week-based columns
    weeks = []
    current_week = []
    start_date = datetime.strptime(daily_commits[0][0], "%Y-%m-%d")
    start_weekday = (start_date.weekday() + 1) % 7 # Align Sunday to index 0
    
    for _ in range(start_weekday): 
        current_week.append(None)
        
    for date_str, count in daily_commits:
        current_week.append((date_str, count))
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
            
    if current_week:
        while len(current_week) < 7: current_week.append(None)
        weeks.append(current_week)

    # Calculate Canvas Size
    width = margin_left + len(weeks) * (cell_size + padding)
    height = margin_top + 7 * (cell_size + padding) + legend_height

    # Start SVG
    svg = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
    
    # Add Month Labels
    last_month = None
    for i, week in enumerate(weeks):
        first_day = next((d for d in week if d), None)
        if first_day:
            dt = datetime.strptime(first_day[0], "%Y-%m-%d")
            month_name = dt.strftime("%b")
            if month_name != last_month:
                x = margin_left + i * (cell_size + padding)
                svg.append(f'<text x="{x}" y="15" style="{text_style}">{month_name}</text>')
                last_month = month_name

    # Add Day Labels
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, label in enumerate(day_labels):
        if i in [1, 3, 5]: 
            y = margin_top + i * (cell_size + padding) + 9
            svg.append(f'<text x="0" y="{y}" style="{text_style}">{label}</text>')

    # Draw Contribution Rectangles
    for i, week in enumerate(weeks):
        x = margin_left + i * (cell_size + padding)
        for j, day in enumerate(week):
            if day:
                date_str, count = day
                y = margin_top + j * (cell_size + padding)
                color = get_color(count)
                svg.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{color}" stroke="rgba(128,128,128,0.05)" stroke-width="0.5"><title>{count} on {date_str}</title></rect>')

    # Draw Legend
    legend_y = height - 15
    # Standard 5-step legend
    legend_colors = [get_color(0), get_color(1), get_color(4), get_color(8), get_color(20)]
    legend_x_start = width - (len(legend_colors) * (cell_size + padding)) - 35
    
    svg.append(f'<text x="{legend_x_start - 30}" y="{legend_y + 9}" style="{text_style}">Less</text>')
    for i, col in enumerate(legend_colors):
        lx = legend_x_start + i * (cell_size + padding)
        svg.append(f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{col}" stroke="rgba(128,128,128,0.05)"></rect>')
    svg.append(f'<text x="{legend_x_start + len(legend_colors) * (cell_size + padding) + 5}" y="{legend_y + 9}" style="{text_style}">More</text>')

    svg.append('</svg>')
    
    with open(output_path, "w") as f:
        f.write("\n".join(svg))

if __name__ == "__main__":
    generate_svg_graph("report.json")