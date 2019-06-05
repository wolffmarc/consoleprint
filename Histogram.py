from consoleprint import RichText
import copy
import math
import string


def _center(string, start, stop, fillchar=' '):
    if len(string) > stop - start:
        return fillchar * (stop - start)
    num_spaces = stop - start - len(string)
    num_spaces_left = int(math.floor(num_spaces * 0.5))
    num_spaces_right = num_spaces - num_spaces_left
    return fillchar * num_spaces_left + string + fillchar * num_spaces_right


def generate_ticks(ticks, numticks, ycoords):
    """
    Generate the list of ticks that will be put on the y axis
    :param ticks: should be 'auto' (automatically generated), 'all' (one tick on each row) or a list of numeric values
    :param numticks: minimum number of ticks to display, only applies to 'auto' mode
    :param ycoords: y coordinates on the figure
    :return: sorted list of ticks
    """
    # Check inputs
    # If too many ticks have been asked for, set ticks to 'all'
    if (ticks == 'auto' and numticks >= len(ycoords)) or (isinstance(ticks, list) and len(ticks) > len(ycoords)):
        ticks = 'all'
    # If ticks is 'all', put a tick on every line
    if ticks == 'all':
        ticks = copy.deepcopy(ycoords)
    # It ticks is 'auto', put at least 'numticks' ticks
    if ticks == 'auto':
        tick_spacing = 5  # default spacing between ticks
        # Decrease the tick spacing progressively until we get the desired number of ticks
        ticks = []
        while len(ticks) < numticks:
            ticks = [ycoords[i] for i in range(tick_spacing - 1, len(ycoords), tick_spacing)]
            tick_spacing -= 1
    # Sort the ticks
    ticks = sorted(y for y in ticks if y <= max(ycoords))
    # Compute the number of characters required to display ticks
    ticks_numchar = max(len(str(NiceNumber(t))) for t in ticks)
    # Compute the Ticks indices on the y axis
    ticks_indices = [min_distance_index(ycoords, t) for t in ticks]
    return ticks, ticks_numchar, ticks_indices


def hcenter(a, b):
    """
    Horizontal centering: centers
    :param a:
    :param b:
    :return:
    """
    # Identify the box with the least and the most characters
    a_is_shortest = a.width() < b.width()
    longest = b if a_is_shortest else a
    shortest = a if a_is_shortest else b
    # Get the max num characters in both lists and add missing whitespaces to keep alignments
    for l in [shortest, longest]:
        strlength = l.width()
        for i in range(len(l)):
            l[i] = l[i].ljust(strlength)
    # Compute size difference
    size_diff = longest.width() - shortest.width()
    if size_diff == 0:
        return a, b
    # Add extra whitespaces
    to_add_left = int(math.floor(0.5 * size_diff))
    for i in range(len(shortest)):
        shortest[i] = ' ' * to_add_left + shortest[i] + ' ' * (size_diff - to_add_left)
    # Return the lists in the same order than the input
    if a_is_shortest:
        return shortest, longest
    else:
        return longest, shortest

def vcenter(a, b):
    # Identify the longest and shortest lists
    a_is_shortest = len(a) < len(b)
    longest = b if a_is_shortest else a
    shortest = a if a_is_shortest else b
    # Get the max num characters in both lists and add missing whitespaces to keep alignments
    for l in [shortest, longest]:
        strlength = l.width()
        for i in range(len(l)):
            l[i] = l[i].ljust(strlength)
    # Compute size difference
    size_diff = len(longest) - len(shortest)
    if size_diff == 0:
        return a, b
    # Add extra strings to the shortest
    shortest.addblank_above(int(math.floor(0.5 * size_diff)))
    shortest.addblank_below(size_diff - int(math.floor(0.5 * size_diff)))
    # Return the lists in the same order than the input
    if a_is_shortest:
        return shortest, longest
    else:
        return longest, shortest



def min_distance_index(x, x0):
    dist = [abs(xx - x0) for xx in x]
    return  dist.index(min(dist))



class NiceNumber:
    """
    A class for displaying good looking numbers in a condensed format
    This is especially useful in figures (labels, ticks) where accuracy is of secondary importance
    """

    def __init__(self, value):
        self._value = value

    def __str__(self):
        # For integer values comprising up to 7 numbers, just return the number itself
        if (isinstance(self._value, int) or math.floor(self._value) == self._value) and abs(self._value) < 1.0e+7:
            return str(int(self._value))
        # We now deal with decimal values
        is_negative = self._value < 0
        value = abs(self._value)
        # Convert values that are too small or too large to scientific notation
        if value < 1.0e-3 or value >= 1.0e+7:
            return is_negative * '-' + "{:.2e}".format(value)
        elif value < 1:
            return (is_negative * '-' + "{:.3f}".format(value)).rstrip('0')
        elif value < 10:
            return (is_negative * '-' + str(round(value, 2))).rstrip('0').rstrip('.')
        elif value < 100:
            return (is_negative * '-' + str(round(value, 1))).rstrip('0').rstrip('.')
        else:
            return is_negative * '-' + str(round(value))


def _getcolor(color, index, y):
    if isinstance(color, str):
        return color
    elif callable(color):
        return color(index, y)
    else:
        raise Exception('unsupported')


class ChartBox:
    """
    Implementation of chart box (i.e. a piece of a chart) as a list of strings
    """

    def __init__(self):
        self._strings = []

    def __getitem__(self, key):
        return self._strings[key]

    def __len__(self):
        return len(self._strings)

    def __setitem__(self, key, value):
        self._strings[key] = value

    def __str__(self):
        out = ''
        for s in self._strings:
            out += s + '\n'
        out = out[:-1]  # remove the last \n character
        return str(out)

    def addblank_above(self, num):
        """
        Add blank rows above the chart box
        :param num: number of blank rows to add
        :return:
        """
        blank = ChartBox()
        for i in range(num):
            blank.append(RichText(' ' * self.width()))
        self._strings = blank._strings + self._strings
        return self

    def addblank_left(self, num):
        """
        Add blank characters on the left of the chart box
        :param num: number of characters to add
        :return:
        """
        for i in range(len(self)):
            self._strings[i] = RichText(' ' * num) + self._strings[i]
        return self

    def addblank_below(self, num):
        """
        Add blank rows below the chart box
        :param num: number of blank rows to add
        :return:
        """
        for i in range(num):
            self.append(RichText(' ' * self.width()))
        return self

    def append(self, new_strings):
        """
        Add new strings to the chart box
        :param new_strings: single string or list of strings to be added
        """
        if isinstance(new_strings, str) or isinstance(new_strings, RichText):
            self._strings.append(new_strings)
        elif isinstance(new_strings, list):
            self._strings += new_strings
        else:
            raise TypeError('cannot append object of type \'' + str(type(new_strings)) + '\'')
        return self

    def bconcat(self, other):
        """
        Bottom-side concatenation with another chart box
        :param other: another chart box
        """
        self._strings = self._strings + copy.deepcopy(other._strings)
        return self

    def lconcat(self, other):
        """
        Left-side concatenation with another chart box
        :param other: another chart box
        """
        for i in range(len(self)):
            self._strings[i] = copy.deepcopy(other._strings[i]) + self._strings[i]
        return self

    def rconcat(self, other):
        """
        Right-side concatenation with another chart box
        :param other:
        :return:
        """
        for i in range(len(self)):
            self._strings[i] = self._strings[i] + copy.deepcopy(other._strings[i])
        return self

    def tconcat(self, other):
        """
        Top-side concatenation with another chart box
        :param other: another chart box
        """
        self._strings = copy.deepcopy(other._strings) + self._strings
        return self

    def isempty(self):
        """
        Return True if the chart box is empty
        :return: True if the chart box is empty, False otherwise
        """
        return len(self._strings) == 0 or self.width() == 0

    def join(self, joinchar):
        new_string = RichText('')
        for s in self._strings:
            new_string += s + joinchar
        new_string = new_string[:-len(joinchar)]
        self._strings = [new_string]
        return self

    def reverse(self):
        """
        Reverse the chart box elements
        """
        self._strings = list(reversed(self._strings))
        return self

    def width(self):
        """
        Compute the width of the chart box (max number of characters in the underlying strings)
        :return: integer
        """
        return 0 if len(self) == 0 else max(len(s) for s in self._strings)


class GenericChart:
    """
    This is the broadest and most generic implementation of a chart
    It only implements standard methods
    """
    def __init__(self, height=20):
        if not isinstance(height, int) or height < 5:
            raise ValueError('height should be an integer value and should be greater than 5')
        self._height = height
        self._left_margin = ' ' * 2
        self.legend = None

    def plot(self, data, legend=None, legendpos='right', numticks=5, ticks='auto', title=None):
        """
        The chart is composed on the following elements

        [                       FIGURE TITLE                        ]
        [             LEGEND if positioned on the top               ]
        [--------------][-------------------------][----------------]
        [              ][                         ][      LEGEND    ]
        [    Y AXIS    ][          FIGURE         ][  if positioned ]
        [              ][                         ][      on the    ]
        [--------------][-------------------------][      right     ]
        [                  FIGURE FOOTER          ][----------------]
        [            LEGEND if positioned on the bottom             ]

        """
        yaxis = self.yaxis(data, ticks, numticks)
        figurebox = self.figurebox(data, ticks)
        legendbox = self.legendbox(legend, legendpos)
        footer = []  # self.figure_footer()

        # Concanate the y axis inside the figure box, then reverse the figure box
        figurebox.lconcat(yaxis).reverse()
        # Concatenate the figure footer inside the figure box
        hasfooter = len(footer) > 0
        if hasfooter:
            exit()
        # If the legend is on the right:
        # - add a few blank characters to separate it from the figure
        # - center the figure and legend boxes vertically
        # - and concatenate them
        if legend is not None and legendpos == 'right':
            legendbox.addblank_left(5)
            figurebox, legendbox = vcenter(figurebox, legendbox)
            figurebox.rconcat(legendbox)
        # If the legend is on the top or the bottom:
        # - put the legend in a single line
        # - add a few blank lines to separate it from the figure
        # - center the figure and the legend boxes horizontally
        # - and concatenate them
        if legend is not None and legendpos in ['top', 'bottom']:
            legendbox.join(RichText(' ' * 5))
            figurebox, legendbox = hcenter(figurebox, legendbox)
            if legendpos == 'top':
                figurebox.tconcat(legendbox.addblank_below(2))
            else:
                figurebox.bconcat(legendbox.addblank_above(2))
        # Create the title box
        hastitle = title is not None and len(title) > 0
        if hastitle:
            titlebox = ChartBox()
            titlebox.append(title if isinstance(title, RichText) else RichText(title, style='bold'))
            titlebox, figurebox = hcenter(titlebox, figurebox)
            figurebox.tconcat(titlebox.addblank_below(2))

        # Add some margins: blank line above the figure and left margin
        figurebox.addblank_above(1)


        # Now actually print the chart
        print(figurebox)

class Bars(GenericChart):
    """
    Standard bar chart
    """

    def __init__(self, color='blue', height=20, showvalues=False, spacing=2, thickness=5):
        super(Bars, self).__init__(height)
        self._color = color
        self._showvalues = showvalues
        self._spacing = spacing
        self._thickness = thickness

    def _barlabels(self):
        """
        Generate labels that will be put beneath bars to designate them
        :return:
        """

    def _legend(self, labels):
        """
        The standard bar chart does not have a need for legends
        :param labels:
        :return: ChartBox object representing the figure, ordered from x=0 to x=max(data)
        """
        return

    def figurebox(self, data, ticks):
        """

        :param data:
        :return:
        """
        num_bars = len(data)
        ycoords, dy = self.ycoordinates(data, ticks)
        # Determine the figure's width
        width = num_bars * self._thickness + (num_bars + 1) * self._spacing
        # Build the figure box and initialize it with the x axis
        figure_box = ChartBox()
        figure_box.append([RichText('-' * width, style='bold')])
        # Draw the figure
        for j in range(self._height):
            y = ycoords[j] - 0.5 * dy  # subtract 0.5 * dy to take the middle of the cell into account for coloring
            s = RichText(' ' * self._spacing)  # add the first spacing
            for i in range(num_bars):
                color = _getcolor(self._color, i, y)
                if y <= data[i]:
                    s += RichText(' ' * self._thickness, bg=color)
                elif j == 0:
                    # On the first row, add underlining to materialize the bar
                    s += RichText(' ' * self._thickness, fg=color, style='underline')
                else:
                    s += ' ' * self._thickness
                s += ' ' * self._spacing
            figure_box.append(s.__clean_style_boxes__())
        # Add bar values
        if self._showvalues:
            # Add an extra line to the figure box
            figure_box.append(RichText(' ' * width))
            # Compute the start and stop indices of each bar along the x axis
            bar_start = [self._spacing + i * (self._thickness + self._spacing) for i in range(num_bars)]
            bar_stop = [i + self._thickness for i in bar_start]
            # Put values above bars
            for i in range(num_bars):
                # Get the height index of the string where the label should be put
                j = ([y - 0.5 * dy > data[i] for y in ycoords] + [True]).index(True)
                # Center the label string in the middle of the bar
                valuestr = _center(str(NiceNumber(data[i])), bar_start[i], bar_stop[i])
                color = _getcolor(self._color, i, ycoords[max(j-1,0)] - 0.5 * dy)
                if j == 0:
                    valuestr = RichText(valuestr, fg=color, style='bold+underline')
                else:
                    valuestr = RichText(valuestr, fg=color, style='bold')
                figure_box[j + 1] = figure_box[j + 1][0:bar_start[i]] + valuestr + figure_box[j + 1][bar_stop[i]:]
        return figure_box

    def legendbox(self, labels, legendpos):
        """
        Simple bar charts don't support legends
        :param labels:
        :return:
        """
        return ChartBox()

    def yaxis(self, data, ticks, numticks):
        """
        Create the y axis
        :param data: data to plot
        :param ticks: y axis ticks or ticks settings
        :param numticks: minimum number of ticks to display, only applies when ticks is 'auto'
        :return: ChartBox representing the y axis, ordered from x=0 to x=max(data)
        """
        # Compute y coordinates
        ycoords, _ = self.ycoordinates(data, ticks)
        # Compute ticks
        if ticks is not None:
            ticks, ticks_numchar, ticks_indices = generate_ticks(ticks, numticks, ycoords)
        else:
            ticks_numchar = 0
            ticks_indices = []
        # Create the y axis
        # Add the margin for the x axis which is located in the first cell of the yaxis list
        yaxis = ChartBox()
        yaxis.append(RichText(' ' * (ticks_numchar-1) + '0|', style='bold'))
        # Build the rest of the y axis
        ticks_cursor = 0  # cursor for keeping track of the next tick to display
        # TODO add comment to explain why we yse height + showvalues
        for j in range(self._height + int(self._showvalues)):
            s = ''
            if ticks is not None:
                if j in ticks_indices:
                    # There is a tick on the current line --> display the tick
                    s += str(NiceNumber(ticks[ticks_cursor])).rjust(ticks_numchar)
                    ticks_cursor += 1
                else:
                    # No tick on current line --> add extra spaces to keep alignment
                    s += ticks_numchar * ' '
            # Add the y axis marker
            s += '|' if j < self._height else ' '
            yaxis.append(RichText(s, style='bold'))
        return yaxis

    def ycoordinates(self, data, ticks=None):
        """
        Compute y coordinates
        :param data: data to plot
        :param ticks: y axis ticks or ticks settings
        :return ycoords: list of y coordinates in ascending order
        :return dy: spacing along the y axis
        """
        # Get the max y value
        # By default, the y max value is just the max value found in the input data
        # However, if ticks have been provided and span further than this value,
        # they should contribute to the computation of the max y value as well
        ymax = max(data)
        if isinstance(ticks, list):
            ymax = max(ymax, max(ticks))
        # Compute the spacing along the y axis
        dy = ymax / (self._height * 1.0)
        # Compute the y coordinates
        ycoords = [i * dy for i in range(1, self._height + 1)]
        # Enforce the max value as last element to prevent round off errors
        ycoords[-1] = ymax
        return ycoords, dy

    def plotDUMMY(self, val, barcolor='blue', ticks=None, numticks=5,
             legend=None, legendposition='bottom',
             thickness=5, spacing=2):

        yaxis = self.yaxis(val, ticks, numticks)
        figure_box = self.figurebox(val, ticks)
        figure_box.lconcat(yaxis).reverse()

        # Generate the legend
        if legend is not None:
            legend_box = self._legend(legend)
            if legendposition in ['top', 'bottom']:
                tmp = ''
                for s in legend_box:
                    tmp += s + ' ' * 5
                tmp = tmp[:-5]
                blank_line = ' ' * len(tmp)
                legend_box = [tmp] + [blank_line] * 2 if legendposition == 'top' else [blank_line] * 2 + [tmp]
                figure_box, legend_box = hcenter(figure_box, legend_box)
            elif legendposition == 'right':
                figure_box, legend_box = vcenter(figure_box, list(reversed(legend_box)))
        else:
            legend_box = []

        # Print the graph
        print(' ')  # blank line
        if legend is not None and legendposition == 'top':
            for s in legend_box:
                print(s)
        #for j in range(len(figure_box)):
        #    row = figure_box[-(j+1)]
        #    if legend is not None and legendposition == 'right':
        #        row += ' ' * 5 + legend_box[j]
        #    print(row)
        print(figure_box)
        if legend is not None and legendposition == 'bottom':
            for s in legend_box:
                print(s)


class StackedBars(Bars):

    def __init__(self, height=20, spacing=2, thickness=5):
        super(StackedBars, self).__init__(height=height, spacing=spacing, thickness=thickness)

    def colorpalette(self):
        """
        Return the list of all colors through which we are going to cycle
        :return: list of colors
        """
        return ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']

    def _coloring(self, y, dictionary, categories):
        """
        This is the bar coloring function
        :param y: current y value
        :param dictionary: dictionary whose values are plotted on the current bar
        :param categories: list of all categories (i.e. dictionary keys)
        :return: color as a member of the list returned by the _colors() method
        """
        for i in range(len(categories)):
            # Compute the y threshold as the cumulative sum of categories values
            if all(k in categories[:i+1] for k in dictionary.keys()):
                # If we have gone through all keys in the current dictionary
                # Set manually the threshold to anything above the sum of values
                # This prevents some round off errors
                threshold = sum(dictionary.values()) * 1.01
            else:
                threshold = sum(dictionary.get(categories[j], 0) for j in range(i+1))
            # If y is below the threshold, use the color associated to the i index
            if y <= threshold:
                return self.colorpalette()[i % len(self.colorpalette())]

    def legendbox(self, labels, legendpos):
        """
        Generate the content of the figure's legend box
        :param labels: legend labels
        :param position: legend position, should be 'top', 'bottom' or 'right'
        :return: list of strings to be placed in the figure's legend box
        """
        legend = ChartBox()
        for i in range(len(labels)):
            color = self.colorpalette()[i % len(self.colorpalette())]
            # Create a small color patch and put the label on its right
            legend.append(RichText(' ' * 3, bg=color) + ' ' + labels[i])
        if legendpos == 'right':
            legend.reverse()
        return legend

    def plot(self, data, legendpos='right', numticks=5, ticks='all', title=None):
        """
        Create the plot
        :param data: list of non-empty dictionaries
        :param ticks: y axis ticks
        :param thickness: bar thickness
        :param spacing: bar spacing
        :return:
        """
        # Form categories by retrieving all keys from all input data
        # We do not want any duplicate here
        categories = []
        for d in data:
            for k in d.keys():
                if k not in categories:
                    categories.append(k)
        categories = sorted(categories)
        # Create the plot
        colorfun = lambda idx, y: self._coloring(y, data[idx], categories)
        super(StackedBars, self).plot(
            [sum(d.values()) for d in data],
            ticks=ticks, barcolor=colorfun, legend=categories, title=title)


class PercentageStackedBars(StackedBars):

    def __init__(self, height=20, spacing=2, thickness=5):
        super(PercentageStackedBars, self).__init__(height, spacing, thickness)

    def plot(self, data, legendpos='right', numticks=5, ticks='all', title=None):
        """
        Create the plot
        :param data: list of non-empty dictionaries
        :param ticks: y axis ticks
        :param thickness: bar thickness
        :param spacing: bar spacing
        :return:
        """
        # Form categories by retrieving all keys from all input data
        # We do not want any duplicates here
        categories = []
        for d in data:
            for k in d.keys():
                if k not in categories:
                    categories.append(k)
        categories = sorted(categories)
        # Convert values to percentages
        for current_dict in data:
            sum_values = sum(current_dict.values())
            for k in current_dict.keys():
                current_dict[k] = current_dict[k] / sum_values * 100.0
        # Set the coloring function
        self._color = lambda idx, y: self._coloring(y, data[idx], categories)
        super(StackedBars, self).plot(
            [100] * len(data),  # with stacked bars, we only plot bars of size 100
            legend=categories, legendpos=legendpos,
            numticks=numticks, ticks=ticks, title=title)














import random

#sb = StackedBars(10)
#sb.plot([{'A': 5, 'B': 12}, {'A': 7, 'C':15}, {'B': 36}, {'C': 4, 'D': 87}])


# Single color bar plot
num_values = random.randint(20, 26)
val = [random.randint(0, 1000) for x in range(num_values)]
legend = []
for i in range(num_values):
    legend.append(random.randint(10, 100) * string.ascii_lowercase[i])
h = Bars(height=20, showvalues=True, spacing=1, thickness=7)
h.plot(val, ticks='auto',  legend=None)


# Bar plot with multiple color levels
data = [random.randint(0, 100) for x in range(random.randint(15,25))]
colorfun = lambda index, y: 'red' if y <= 50 else 'yellow' if y <= 70 else 'green'
bars = Bars(height=10, color=colorfun, spacing=1, thickness=3)
bars.plot(data, ticks='auto', numticks=5)
bars.plot(data, ticks=list(range(10, 110, 10)))
bars = Bars(height=12, color=colorfun, spacing=1, thickness=3)
bars.plot(data, ticks=list(range(10, 130, 10)))
bars = Bars(height=10, color=colorfun, spacing=1, thickness=3, showvalues=True)
bars.plot(data, ticks='auto', numticks=5)
bars.plot(data, ticks=list(range(10, 110, 10)))
bars = Bars(height=12, color=colorfun, spacing=1, thickness=3, showvalues=True)
bars.plot(data, ticks=list(range(10, 130, 10)))



# Stacked bars plot
bu_names = ['Agos', 'Sofinco', 'Creditplus', 'CACF NL', 'Credibom', 'Wafasalaf', 'GAC', 'CACF Bankia']
bu_activity_probability = [0.7, 0.3, 0.5, 0.1, 0.8, 0.2, 0.7, 0.9]
num_values = random.randint(25, 30)
data = []
for i in range(num_values):
    new_dict = {}
    while len(new_dict) == 0:
        for j in range(len(bu_names)):
            if random.random() <= bu_activity_probability[j]:
                new_dict[bu_names[j]] = random.randint(1, 1e6)
    data.append(new_dict)
#sb = StackedBars(20)
#sb.plot(data, spacing=1, thickness=3)

sb = PercentageStackedBars(height=20, spacing=1, thickness=3)
sb.plot(data, legendpos='top', title='Percentage stacked bars with legend above the figure'.title())
sb.plot(data, legendpos='right', title='Percentage stacked bars with legend on the right'.title())
sb.plot(data, legendpos='bottom', title='Percentage stacked bars with legend below the figure'.title())




