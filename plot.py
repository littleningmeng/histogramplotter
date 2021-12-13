# -*- coding: utf-8 -*-
import re
import click
import pandas as pd
import numpy as np
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import column
from bokeh.models import HoverTool
from bokeh.io import show


def parse_histogram_file(filepath):
    regex = re.compile(r"\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)")
    lines = [line for line in open(filepath, "r", encoding="utf-8") if re.match(regex, line)]
    values = [re.findall(regex, line)[0] for line in lines]
    pctles = [(float(v[0]), float(v[1]), int(v[2]), float(v[3])) for v in values]
    pre_total = 0
    delays = []
    for delay, _, total, _ in pctles:
        count = total - pre_total
        if count > 0:
            delays += [float(delay)] * count
        pre_total = total
    percentiles = pd.DataFrame(pctles, columns=["Latency", "Percentile", "TotalCount", "inv-pct"])
    
    return delays, percentiles
    

def plot(histogram_file, max_delay=2000, delay_step=10, ):
    delays, data = parse_histogram_file(histogram_file)
    hist, edges = np.histogram(delays, bins=max_delay // delay_step, range=[0, max_delay])
    delays = pd.DataFrame({"delay": hist, "left": edges[:-1], "right": edges[1:]})
    src = ColumnDataSource(delays)
    f1 = figure(plot_width=1200, plot_height=400, title = "Latency distribution (x:Percentage, y:Latency)", x_axis_label="Percentage", y_axis_label="Latency ms", tooltips=[("Percentage", "@x %"), ("Latency", "@y{0.00}ms")])
    f1.line(data["Percentile"] * 100, data["Latency"], color="red", line_width=2)
    f2 = figure(plot_width=1200, plot_height=400, title = "Latency distribution (x:Latency, y:Count)", x_axis_label="Latency ms", y_axis_label="Count")
    f2.add_tools(HoverTool(tooltips=[("Count", "@delay"), ("Latency range", "@left{0.00}ms - @right{0.00}ms")]))
    f2.quad(source=src, bottom=0, top="delay", left="left", right="right", fill_color="green", line_color="white")
    # Show the plot
    show(column(f1, f2))


@click.command()
@click.option("-H", "--histogram-file", required=True, help="the histogram file")
def main(histogram_file):
    plot(histogram_file)
    
    
if __name__ == "__main__":
    main()
