import numpy as np
from scipy.stats.kde import gaussian_kde
from bokeh.io import show
from bokeh.layouts import row, gridplot
from bokeh.models import RangeTool, FuncTickFormatter, Div
from bokeh.plotting import figure, output_file
from bokeh.palettes import Category20


class DeltaPlot:

    def __init__(self, sliding_window, colors=None):
        self.sw = sliding_window
        self.colors = colors
        # helper variables
        self.plots_path = 'results/plots/'
        self.groupby_subset = self.sw.window_data.groupby('subset')
        self.groupby_subset_filtered = self.sw.window_data_filtered.groupby(
            'subset')
        self.parameter_text = self.make_parameter_text()
        self.n_windows = self.num_windows(self.sw.window_data)
        self.n_windows_filtered = self.num_windows(
            self.sw.window_data_filtered)
        # append x-ticks for dot plots
        self.add_x_ticks(self.sw.window_data, self.n_windows)
        self.add_x_ticks(self.sw.window_data_filtered, self.n_windows_filtered)

    def make_parameter_text(self):
        target_text = ', '.join(self.sw.target)
        window_size_text = f"Window size: {self.sw.window_size}"
        is_plural = 's' if self.sw.target.size > 1 else ''
        stride_text = f"Window stride: {self.sw.stride}"
        return f"Target{is_plural}: {target_text}</br>{window_size_text}</br>{stride_text}"

    def num_windows(self, df):
        return df.shape[0] / self.sw.n_subset

    def add_x_ticks(self, df, n_windows):
        window_range = np.arange(1, n_windows+1)
        df['x_ticks'] = np.repeat(window_range, self.sw.n_subset)


    def make_color_palette(self):
        if not self.colors:
            self.colors = Category20[20]
        color_map = {name: color for name,
                     color in zip(self.sw.subset_names, self.colors)}
        return self.sw.window_data['subset'].map(color_map)

    def dot_plot(self, groupby_subset, tools, x_range):
        tooltips = [
            ("Window position", "@window_start")
        ]
        p = figure(
            height=400,
            width=1000,
            tools=tools,
            toolbar_location="right",
            x_axis_location="below",
            background_fill_color="#efefef",
            x_range=x_range,
            tooltips=tooltips)


        group_count = self.sw.n_subset - 1
        group_count_inv = 0
        for name, group in groupby_subset:
            p.segment('x_ticks', 0, 'x_ticks', '%s_delta' % self.sw.subset_names[group_count], line_color='#bdbdbd',
                      line_width=1, legend_label='%s minus %s' % (self.sw.subset_names[group_count_inv], self.sw.subset_names[group_count]), source=group)
            group_count = group_count - 1
            group_count_inv = group_count_inv + 1

        circles = []
        group_count = self.sw.n_subset - 1
        group_count_inv = 0
        for name, group in groupby_subset:
            circles.append(p.circle('x_ticks', '%s_delta' % self.sw.subset_names[group_count],
                                    size=7,
                                    legend_label='%s minus %s' % (self.sw.subset_names[group_count_inv], self.sw.subset_names[group_count]),
                                    color='color',
                                    muted_color='color',
                                    muted_alpha=0.2,
                                    source=group))
            group_count = group_count - 1
            group_count_inv = group_count_inv + 1

        p.legend.click_policy = "hide"
        p.hover.renderers = circles
        p.yaxis.axis_label = 'Delta window frequency mean'
        return p


    def format_x_axis(self, p, df):
        x_label = {key: value for key, value in zip(
            df['x_ticks'], df['window_start'])}
        p.xaxis.formatter = FuncTickFormatter(code="""
            var labels = %s;
            return labels[tick] || tick;
            """ % x_label)

    def sliding_panel(self, p, df):
        self.format_x_axis(p, df)
        select = figure(
            height=150,
            width=1000,
            x_range=(0, df['x_ticks'].iloc[-1]+1),
            y_range=p.y_range,
            y_axis_type=None,
            tools="save",
            toolbar_location=None,
            background_fill_color="#efefef"
        )
        select.xaxis.axis_label = 'Window position'
        self.format_x_axis(select, df)
        range_tool = RangeTool(x_range=p.x_range)
        range_tool.overlay.fill_color = "navy"
        range_tool.overlay.fill_alpha = 0.2
        group_count = self.sw.n_subset - 1
        for _, group in self.groupby_subset:
            select.circle('x_ticks', '%s_delta' % self.sw.subset_names[group_count],
                          color=group['color'].values[0], alpha=0.6, source=group)
            group_count = group_count - 1
        select.ygrid.grid_line_color = None
        select.add_tools(range_tool)
        select.toolbar.active_multi = 'auto'
        return select

    def sliding_window_plot(self, df):
        output_file("results/plots/delta_plot.html",
                    title="Sliding window plot")
        initial_panel_size = int(self.n_windows * 0.1)
        p = self.dot_plot(self.groupby_subset, [
                          "xpan", "save"], (0, initial_panel_size))
        select = self.sliding_panel(p, df)
        div = Div(text=self.parameter_text, width=200,
                  height=100)
        grid = gridplot([[p, div], [select, None]], merge_tools=True)
        show(grid)

    def make_plots(self):
        self.sw.window_data['color'] = self.make_color_palette()
        self.sw.window_data_filtered['color'] = self.make_color_palette()
        self.sliding_window_plot(self.sw.window_data)
