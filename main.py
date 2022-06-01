from machine import Timer
import decisiontree
import time
temp_c, temp_f, pressu = 0,0,0
def read_weather():
    bme = BME280.BME280(i2c=i2c)
    global temp_c; global temp_f; global pressu
    global x; global y
    temp_c = bme.read_temperature()/100.0 - 1.0
    temp_f = str(round((bme.read_temperature()/100.0 - 1.0) * (9/5) + 32, 2))
    pressu = str(bme.pressure)
    x.append(temp_c)
    y.append("")
    print("updated weather")
    
def web_page():
    temp_c_s = str(temp_c)
    
    s = 0
    for i in x:
        s += i

    s /= len(x)
    s = str(round(s, 2))
    
    pred = t.predict([{'t1': x[-3], 't2': x[-2], 't3': x[-1]}]) if t else [0]
    
    html = """
    <html><head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,"><style>body { text-align: center; font-family: "Trebuchet MS", Arial;}
    table { border-collapse: collapse; width:50%; margin-left:auto; margin-right:auto; }
    th { padding: 12px; background-color: black; color: white; }
    tr { border: 1px solid #ddd; padding: 12px; }
    tr:hover { background-color: #bcbcbc; }
    td { border: none; padding: 12px;}
    .sensor { color:black; font-weight: bold; background-color: white; padding: 1px;
    </style></head><body><h1></h1>
    <table>
    <tr><th>POMIAR</th><th>WARTOSC</th></tr>
    <tr><td>Temperatura w Celsiuszach</td><td><span class="sensor"> """ + temp_c_s + """ C</span></td></tr>
    <tr><td>Temperatura w Fahrenheitach</td><td><span class="sensor"> """ + temp_f + """ F</span></td></tr>
    <tr><td>Cisnienie</td><td><span class="sensor"> """ + pressu + """</span></td></tr>
    <tr><td>Srednia temperatura</td><td><span class="sensor"> """ + s + """ C</span></td></tr>
    <tr><td><canvas id="line-chart" style="width:100%;max-width:400px;margin-left:auto; margin-right:auto;"></canvas></td><td><span class="sensor">Wykres<br>temperatur</span></td></tr>
    <script>
    new Chart(document.getElementById("line-chart"), {
    type: 'line',
    data: {
        labels: """ + str(y) + """,
        datasets: [{ 
            data: """ + str(x) + """,
            label: "Temperatura",
            borderColor: "#3e95cd",
            fill: false
        }, { 
            data: """ + str(pred) + """,
            label: "Predykcja",
            borderColor: "#3e9520",
            fill: false
        }
        ]
    },
    });
    </script>
    </body></html>
    """
    return html


x = []
y = []
preds = []


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
print("init")
timer = Timer(-1)
read_weather()
t = None
while True:
  try:
    timer.init(period=2000, mode=Timer.PERIODIC, callback=lambda _:read_weather())
    if gc.mem_free() < 102000:
      gc.collect()
    print("waiting for request")
    conn, addr = s.accept()
    timer.deinit()
    if len(x) > 2:
        t = decisiontree.MyTreeRegressor(3)
        xs = {'t1': x[1:-4], 't2': x[2:-3], 't3': x[3:-2]}
        t.fit(xs, x[4:])
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')






