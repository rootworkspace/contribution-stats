import json
from datetime import datetime, timedelta

def get_color(count):
    """Maps commit counts to a vibrant palette."""
    colors = [
        "rgba(45, 45, 48, 1)",      # 0
        "rgba(255, 105, 180, 0.7)",  # 1-2
        "rgba(190, 80, 255, 0.8)",   # 3-5
        "rgba(90, 130, 255, 0.9)",   # 6-15
        "rgba(0, 220, 255, 1.0)"     # 16+
    ]
    if count == 0: return colors[0]
    if count <= 2: return colors[1]
    if count <= 5: return colors[2]
    if count <= 15: return colors[3]
    return colors[4]

def generate_svg_graph(json_path, output_path="contribution_graph.svg"):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found.")
        return

    daily_commits = sorted(data["daily_commits"].items())
    
    # Layout Constants
    cell_size, padding = 12, 3
    margin_left, margin_top = 35, 30
    legend_height = 35
    
    text_style = "fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 10px;"
    
    # Process data into weeks
    weeks = []
    current_week = []
    start_date = datetime.strptime(daily_commits[0][0], "%Y-%m-%d")
    start_weekday = (start_date.weekday() + 1) % 7 
    
    for _ in range(start_weekday): current_week.append(None)
    for date_str, count in daily_commits:
        current_week.append((date_str, count))
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    if current_week:
        while len(current_week) < 7: current_week.append(None)
        weeks.append(current_week)

    width = margin_left + len(weeks) * (cell_size + padding) + 20
    height = margin_top + 7 * (cell_size + padding) + legend_height

    # Start SVG
    svg = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background-color: #0d1117; border-radius: 6px;" shape-rendering="geometricPrecision">']
    
    # Brighter Outline Logic
    def get_rect_svg(x, y, count, date_str=None):
        color = get_color(count)
        stroke_color = "rgba(255, 255, 255, 0.05)" if count == 0 else "rgba(255, 255, 255, 0.3)"
        
        # Ensure title content is simple and safe for XML
        title_tag = f"<title>{count} contributions on {date_str}</title>" if date_str else ""
        
        return f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{color}" stroke="{stroke_color}" stroke-width="1">{title_tag}</rect>'

    # Add Month Labels
    last_month = None
    for i, week in enumerate(weeks):
        first_day = next((d for d in week if d), None)
        if first_day:
            dt = datetime.strptime(first_day[0], "%Y-%m-%d")
            month_name = dt.strftime("%b")
            if month_name != last_month:
                x = margin_left + i * (cell_size + padding)
                svg.append(f'<text x="{x}" y="20" style="{text_style}">{month_name}</text>')
                last_month = month_name

    # Add Day Labels
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, label in enumerate(day_labels):
        if i in [1, 3, 5]: 
            y = margin_top + i * (cell_size + padding) + 10
            svg.append(f'<text x="5" y="{y}" style="{text_style}">{label}</text>')

    # Draw Rectangles
    for i, week in enumerate(weeks):
        x = margin_left + i * (cell_size + padding)
        for j, day in enumerate(week):
            y = margin_top + j * (cell_size + padding)
            if day:
                date_str, count = day
                svg.append(get_rect_svg(x, y, count, date_str))
            else:
                svg.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="transparent" />')

    # Draw Legend
    legend_y = height - 20
    legend_vals = [0, 2, 5, 15, 20]
    legend_x_start = width - (len(legend_vals) * (cell_size + padding)) - 50
    
    svg.append(f'<text x="{legend_x_start - 35}" y="{legend_y + 10}" style="{text_style}">Less</text>')
    for i, val in enumerate(legend_vals):
        lx = legend_x_start + i * (cell_size + padding)
        svg.append(get_rect_svg(lx, legend_y, val))
    svg.append(f'<text x="{legend_x_start + len(legend_vals) * (cell_size + padding) + 5}" y="{legend_y + 10}" style="{text_style}">More</text>')

    svg.append('</svg>')

    with open(output_path, "w") as f:
        f.write("\n".join(svg))
    print(f"Graph generated at {output_path}")

if __name__ == "__main__":
    generate_svg_graph("report.json")