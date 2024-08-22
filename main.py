import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import datetime
import threading
import time as time_lib
import win32api, win32con

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Layout of the app
app.layout = html.Div([
    html.H1("Mouse Jiggler Control Panel"),

    dcc.Slider(
        id='jiggle-frequency-slider',
        min=1,
        max=60,
        step=1,
        value=27,
        marks={i: str(i) for i in range(1, 61)},
        tooltip={"placement": "bottom", "always_visible": True},
    ),

    dcc.Dropdown(
        id='run-duration-dropdown',
        options=[
            {'label': '1 Hour', 'value': 60},
            {'label': '1.5 Hours', 'value': 90},
            {'label': '2 Hours', 'value': 120},
            {'label': '2.5 Hours', 'value': 150},

            {'label': '3 Hours', 'value': 180},
            {'label': '4 Hours', 'value': 240},
            {'label': '5 Hours', 'value': 300},
            {'label': '6 Hours', 'value': 360},
            {'label': '7 Hours', 'value': 420},
            {'label': '8 Hours', 'value': 480},
        ],
        value=60,
        clearable=False,
    ),

    html.Button('Start', id='start-button', n_clicks=0),
    html.Button('Stop', id='stop-button', n_clicks=0),

    html.Div(id='status'),
    html.Div(id='current-time'),
    html.Div(id='runtime'),
])

# Define global variables
running = False
start_time = None
stop_event = threading.Event()


def jiggler_thread(frequency, duration):
    global running
    global start_time
    global stop_event

    running = True
    start_time = datetime.datetime.now()
    stop_event.clear()

    while running and not stop_event.is_set():
        current_time = datetime.datetime.now()
        current_seconds = current_time.second

        if current_seconds % frequency == 0:
            win32api.SetCursorPos((10, 10))
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 10, 10, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 10, 10, 0, 0)

        if (current_time - start_time).total_seconds() >= duration * 60:
            running = False

        time_lib.sleep(1)

    if not stop_event.is_set():
        print("Jiggling completed.")


@app.callback(
    Output('status', 'children'),
    Output('current-time', 'children'),
    Output('runtime', 'children'),
    Input('start-button', 'n_clicks'),
    Input('stop-button', 'n_clicks'),
    State('jiggle-frequency-slider', 'value'),
    State('run-duration-dropdown', 'value')
)
def update_output(start_clicks, stop_clicks, frequency, duration):
    global running
    global start_time
    global stop_event

    ctx = dash.callback_context
    if not ctx.triggered:
        return "Click Start to begin.", "", ""

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'start-button' and not running:
        threading.Thread(target=jiggler_thread, args=(frequency, duration)).start()
        return "Jiggler is running.", f"Current Time: {datetime.datetime.now().strftime('%H:%M:%S')}", f"Runtime: {datetime.datetime.now() - start_time if start_time else datetime.timedelta()}"

    elif trigger == 'stop-button' and running:
        running = False
        stop_event.set()
        return "Jiggler stopped.", "", f"Runtime: {datetime.datetime.now() - start_time if start_time else datetime.timedelta()}"

    return ("Jiggler is running." if running else "Click Start to begin.",
            f"Current Time: {datetime.datetime.now().strftime('%H:%M:%S')}",
            f"Runtime: {datetime.datetime.now() - start_time if start_time else datetime.timedelta()}"
            )


if __name__ == '__main__':
    app.run_server(debug=True)
