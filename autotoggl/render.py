import html
import os
from datetime import datetime, timedelta


COLORS = [
    '#f44336',
    '#2196f3',
    '#4caf50',
    '#9c27b0',
    '#e91e63',
    '#673ab7',
    '#3f51b5',
    '#03a9f4',
    '#00bcd4',
    '#009688',
    '#8bc34a',
    '#cddc39',
    '#ffeb3b',
    '#ffc107',
    '#ff9800',
    '#ff5722',
    '#795548',
    '#607d8b',
]


HTML_START = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#111111">
<title>autotoggl</title>
<style>
#container {{
    display: inline-block;
    min-width: 100%;
    height: 1em;
    background: #9e9e9e;
    position: relative;
}}
#hover {{
    min-height: 200px;
}}
#hours {{
    position: relative;
    min-width: 100%;
    height: 1em;
}}
.hour {{
    position: absolute;
}}
div{{
    padding:0;
    margin:0;
}}
.event {{
    height: 1em;
    position: absolute;
}}
.key-item {{
    height:1em;
    display: flex;
    flex-direction: row;
    padding: 4px 0;
}}
.key-color {{
    width: 1em;
}}
.key-name {{
    margin-left: 6px;
}}
{styles}
</style>
</head>
<body>
<header>{start} -> {end}<br/>{events} events</header>
<div id="key">{key}</div>
<div id="hours">{hours}</div>
<div id="container">
'''


HTML_END = '''
</div>
<div id="hover"></div>
<script>
function show(text) {
    console.log(text);
    document.getElementById('hover').innerHTML = text;
}
</script>
</body>
</html>
'''


HTML_EVENT = (
    '<div class="event {project}" '
    'style="left:{start}%;width:{width}%" '
    'onmouseover="show(\'{about}\')"></div>'
)


HTML_ABOUT = (
    '{project} - {description}: {start} -> {end} [{tags}]'
)


def render_events(events, file=os.path.expanduser('~/autotoggl/preview.html')):
    start = events[0].start
    end = events[-1].start + events[-1].duration

    total_width = end - start

    project_colors = {}
    content = ''

    for e in events:
        project = e.project
        if not project:
            continue
        if project not in project_colors:
            project_colors[project] = COLORS[len(project_colors)]
        content += (
            HTML_EVENT.format(
                project=html.escape(project),
                start=round(((e.start - start) / total_width * 100), 2),
                width=round((e.duration / total_width * 100), 2),
                about=html.escape(HTML_ABOUT.format(
                    project=html.escape(_sanitize(e.project)),
                    description=html.escape(_sanitize(e.description)),
                    start=_format_timestamp(e.start),
                    end=_format_timestamp(e.start + e.duration),
                    tags=', '.join([f'#{t}' for t in e.tags])
                ))))

    styles = [f'.{x} {{background:{y};}}'for x, y in project_colors.items()]
    key = [_key(x) for x in project_colors]
    with open(file, 'w') as f:
        f.write(
            HTML_START.format(
                start=html.escape(datetime.fromtimestamp(start).isoformat()),
                end=html.escape(datetime.fromtimestamp(end).isoformat()),
                events=len(events),
                styles=''.join(styles),
                key=''.join(key),
                hours=_hours(start, end)))
        f.write(content)
        f.write(HTML_END)


def _key(project):
    return '''
    <div class="key-item">
        <div class="key-color {project}"></div><div class="key-name">{project}</div>
    </div>
    '''.format(project=html.escape(project))


def _hours(start, end):
    width = end - start
    start_dt = datetime.fromtimestamp(start)
    end_dt = datetime.fromtimestamp(end)
    hours = []

    start_hour = start_dt.hour
    end_hour = end_dt.hour + 1
    if end_hour < start_hour:
        end_hour += 24

    for h in range(start_hour, end_hour):
        dt = start_dt.replace(minute=0, second=0, hour=h % 24)
        if h > 23:
            dt += timedelta(days=1)
        position = round((dt.timestamp() - start) / width * 100, 2)
        hours.append(
            '''<div class="hour" style="left:{start}%;">{hour}</div>'''
            .format(
                start=position,
                hour='|{}'.format(h % 24)
            ))
    return ''.join(hours)


def _sanitize(path):
    path = path or ''
    return path.replace('\\', '/')


def _format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M')
