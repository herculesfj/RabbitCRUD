import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import pika, threading, json
import eventlet
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

eventlet.monkey_patch()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
MONITOR_QUEUE = "monitor_queue"
REQUEST_QUEUE = "crud_queue"

# In-memory stats
monitor_stats = {
    "workers": {},  # worker_id -> {"processed": int, "last_seen": datetime, "errors": int}
    "total_processed": 0,
    "queue_length": 0,
    "crud_counts": {"create": 0, "read": 0, "update": 0, "delete": 0},
    "last_messages": []
}

# Mongo client for optional persistence of monitor events
mongo = MongoClient(MONGO_URI)
db = mongo["crud_db"]
monitor_col = db.get_collection("monitor_events")

WORKER_TIMEOUT = 10
ALERT_QUEUE = 20

def consume_monitor_queue():
    params = pika.ConnectionParameters(host=RABBITMQ_HOST)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(queue=MONITOR_QUEUE, durable=True)
    def callback(ch_, method, props, body):
        try:
            data = json.loads(body)
            worker = data.get("worker_id")
            action = data.get("action")
            status = data.get("status", "success")
            ts_str = data.get("timestamp")
            ts = datetime.fromisoformat(ts_str) if ts_str else datetime.utcnow()
            # update in-memory
            if worker not in monitor_stats["workers"]:
                monitor_stats["workers"][worker] = {"processed": 0, "last_seen": ts, "errors": 0}
            monitor_stats["workers"][worker]["processed"] += 1
            monitor_stats["workers"][worker]["last_seen"] = ts
            if status != "success":
                monitor_stats["workers"][worker]["errors"] = monitor_stats["workers"][worker].get("errors",0) + 1
            monitor_stats["total_processed"] += 1
            if action in monitor_stats["crud_counts"]:
                monitor_stats["crud_counts"][action] += 1
            entry = {"worker": worker, "action": action, "status": status, "timestamp": ts.isoformat(), "error": data.get("error")}
            monitor_stats["last_messages"].insert(0, entry)
            monitor_stats["last_messages"] = monitor_stats["last_messages"][:50]
            # persist optional
            try:
                monitor_col.insert_one(entry)
            except Exception:
                pass
        except Exception as e:
            print("monitor consume error", e)
        finally:
            ch_.basic_ack(delivery_tag=method.delivery_tag)
    ch.basic_consume(queue=MONITOR_QUEUE, on_message_callback=callback)
    ch.start_consuming()

def poll_queue_length():
    params = pika.ConnectionParameters(host=RABBITMQ_HOST)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    while True:
        try:
            q = ch.queue_declare(queue=REQUEST_QUEUE, passive=True)
            monitor_stats["queue_length"] = q.method.message_count
        except Exception:
            monitor_stats["queue_length"] = 0
        eventlet.sleep(2)

# start background threads
threading.Thread(target=consume_monitor_queue, daemon=True).start()
threading.Thread(target=poll_queue_length, daemon=True).start()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

app.layout = dbc.Container([
    html.H1("RabbitCRUDPro - Monitor Dashboard", style={"textAlign":"center", "marginTop":"10px"}),
    dcc.Interval(id="interval-update", interval=2000),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Fila (crud_queue)"), dbc.CardBody(html.H3(id="queueCount"))], id="card-queue"), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("Total Processado"), dbc.CardBody(html.H3(id="totalProcessed"))]), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("Workers Ativos"), dbc.CardBody(html.H3(id="workersCount"))]), width=4)
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="workerGraph"), width=6),
        dbc.Col(dcc.Graph(id="crudGraph"), width=6)
    ]),
    dbc.Row([
        dbc.Col(html.H4("Últimas Mensagens (últimas 50)")),
        dbc.Col(html.Div(id="alerts"), style={"textAlign":"right"})
    ]),
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id="lastMessagesTable",
            columns=[{"name":"worker","id":"worker"},{"name":"action","id":"action"},{"name":"status","id":"status"},{"name":"timestamp","id":"timestamp"},{"name":"error","id":"error"}],
            data=[],
            page_size=10,
            style_data_conditional=[]
        ), width=12)
    ])
], fluid=True)

from dash import Input as DashInput, Output as DashOutput

@app.callback(
    [DashOutput("queueCount","children"),
     DashOutput("card-queue","color"),
     DashOutput("totalProcessed","children"),
     DashOutput("workersCount","children"),
     DashOutput("workerGraph","figure"),
     DashOutput("crudGraph","figure"),
     DashOutput("lastMessagesTable","data"),
     DashOutput("lastMessagesTable","style_data_conditional"),
     DashOutput("alerts","children")],
    [DashInput("interval-update","n_intervals")]
)
def update(n):
    queue = monitor_stats["queue_length"]
    total = monitor_stats["total_processed"]
    workers = monitor_stats["workers"]
    workers_count = len(workers)

    # queue color
    if queue > ALERT_QUEUE:
        color = "danger"
    elif queue > ALERT_QUEUE/2:
        color = "warning"
    else:
        color = "success"

    # worker chart
    labels = list(workers.keys())
    values = [w["processed"] for w in workers.values()]
    now = datetime.utcnow()
    colors = []
    for w in workers.values():
        last_seen = w.get("last_seen", now)
        diff = (now - last_seen).total_seconds()
        colors.append("red" if diff > WORKER_TIMEOUT else "#0077b6")
    worker_fig = {"data":[{"x": labels, "y": values, "type":"bar", "marker":{"color": colors}}], "layout":{"title":"Operações por Worker"}}

    # crud fig
    crud_labels = list(monitor_stats["crud_counts"].keys())
    crud_values = list(monitor_stats["crud_counts"].values())
    crud_fig = {"data":[{"labels": crud_labels, "values": crud_values, "type":"pie"}], "layout":{"title":"CRUD Counts"}}

    # build table and style conditionals for errors
    data = monitor_stats["last_messages"]
    style_cond = []
    for i, row in enumerate(data):
        if row.get("status") != "success":
            style_cond.append({"if":{"row_index":i}, "backgroundColor":"#ff6b6b", "color":"white"})
    # alerts
    alerts = []
    if queue > ALERT_QUEUE:
        alerts.append(html.Span("⚠️ Fila crítica", style={"color":"red", "fontWeight":"bold", "marginRight":"10px"}))
    # workers inactive
    inactive = [w for w, v in workers.items() if (datetime.utcnow() - v.get("last_seen", datetime.utcnow())).total_seconds() > WORKER_TIMEOUT]
    if inactive:
        alerts.append(html.Span(f"⚠️ Workers inativos: {', '.join(inactive)}", style={"color":"red", "fontWeight":"bold"}))
    return queue, color, total, workers_count, worker_fig, crud_fig, data, style_cond, alerts

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=6000, debug=False)
