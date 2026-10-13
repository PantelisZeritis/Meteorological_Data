import psycopg2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_connection():
    try:
        return psycopg2.connect(
            database = "sensors",
            user = "sensors",
            password = "DKM-sensors37",
            host = "localhost",
            port = 5432,
        )
    except:
        return False


conn = get_connection()

def exec():
    cursor = conn.cursor()

    query = "SELECT city, day, hour, AVG(temperature) as temperature" \
            " FROM okairosdata" \
            " WHERE EXTRACT(YEAR FROM timecrawl) = 2025" \
                " AND SPLIT_PART(day, '/', 2) = '5'" \
                " AND city = 'Τρίπολη'" \
                " AND hour = '12:00'" \
                " GROUP BY day, hour, city" \
            " ORDER BY day ASC"
    
    query2 = "SELECT city, day, hour, AVG(temperature) as temperature" \
        " FROM meteodata" \
        " WHERE EXTRACT(YEAR FROM timecrawl) = 2025" \
            " AND SPLIT_PART(day, '/', 2) = '5'" \
            " AND city = 'ΤΡΙΠΟΛΗ'" \
            " AND hour = '12:00'" \
            " GROUP BY day, hour, city" \
        " ORDER BY CAST(SPLIT_PART(day, '/', 1) AS INTEGER) ASC"

    df_forecast = pd.read_sql(query, conn)
    df_live = pd.read_sql(query2, conn)
    
    df_forecast['day_num'] = df_forecast['day'].str.split('/').str[0].astype(int)

    df_live['day_num'] = df_live['day'].str.split('/').str[0].astype(int)

    max_forecast = df_forecast['temperature'].max()
    max_live = df_live['temperature'].max()

    min_forecast = df_forecast['temperature'].min()
    min_live = df_live['temperature'].min()

    plot_max = max(max_forecast, max_live)
    plot_min = min(min_forecast, min_live)

    days = list(range(1, 32))
    temperatures = np.linspace(plot_max, plot_min, 31)

    plt.figure(figsize = (12, 5))
    plt.plot(df_forecast['day_num'], df_forecast['temperature'], marker = 'o', label = 'Okairos.gr')
    plt.plot(df_live['day_num'], df_live['temperature'], marker = 'x', linestyle = '--', label = 'Meteo.gr')

    plt.xlabel('Day of month')
    plt.xticks(days)
    plt.yticks(temperatures)
    plt.ylabel('Temperature (°C)')
    plt.title('Forecast at 12:00 (Meteo.gr vs Okairos.gr) - May Tripoli 2025')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('plot.png')

    conn.close()

if conn:
    print("Connection to the PostgreSQL established successfully.")

    exec()
else:
    print("Connection to the PostgreSQL encountered and error.")
