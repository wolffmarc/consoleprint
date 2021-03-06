from abc import ABC, abstractmethod
from consoleprint import RichText
import copy
import math

# TODO LIST
# TODO add option for displaying labels beneath bars
# TODO add input data checks


def get_tick_indices(tickmode, numticks, coords):
    """
    Ticks on the axis are a subset of the axis coordinates
    This function returns the indices of y coordinates on which a tick should be displayed
    :param tickmode: should be 'auto' (automatically generated) or 'all'
    :param numticks: minimum number of ticks to display, only applies to 'auto' mode
    :param coords: list of coordinates along the axis
    :return indices: ticks indices in the input list of y coordinates
    :return numchar: maximum number of characters required to display ticks, this is useful to preserve alignments
    """
    if tickmode == 'all' or (tickmode == 'auto' and numticks >= len(coords)):
        # Put a tick in front of each row
        indices = list(range(len(coords)))
    else:
        # It tickmode is 'auto', put at least 'numticks' ticks
        tick_spacing = 5  # default spacing between ticks
        # Decrease the tick spacing progressively until we get the desired number of ticks
        indices = []
        while len(indices) < numticks:
            indices = list(range(0, len(coords), tick_spacing))
            tick_spacing -= 1
    # Compute the number of characters required to display ticks
    numchar = max(len(str(NiceNumber(coords[i]))) for i in indices)
    return indices, numchar


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
        return str(RichText('\n').join(self._strings))

    def laddblank(self, num):
        """
        Add blank characters on the left of the chart box
        :param num: number of characters to add
        :return:
        """
        for i in range(len(self)):
            self._strings[i] = RichText(' ' * num) + self._strings[i]
        return self

    def raddblank(self, num):
        """
        Add blank characters on the right of the chart box
        :param num: number of characters to add
        :return:
        """
        for i in range(len(self)):
            self._strings[i] = self._strings[i] + RichText(' ' * num)
        return self

    def baddblank(self, num):
        """
        Add blank rows to the bottom of the chart box
        :param num: number of blank rows to add
        :return:
        """
        self.append([RichText(' ' * self.width())] * num)
        return self

    def taddblank(self, num):
        """
        Add blank rows to the top of the chart box
        :param num: number of blank rows to add
        :return:
        """
        blank = ChartBox()
        blank.append([RichText(' ' * self.width())] * num)
        self._strings = blank._strings + self._strings
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

    def hcenter(self, other):
        """
        Horizontal centering: centers the 'self' and 'other' chart boxes horizontally
        :param other: other chart box
        :return: 'self' and 'other' inputs in the same order
        """
        # Identify the box with the least and the most characters
        self_is_shortest = self.width() < other.width()
        longest = other if self_is_shortest else self
        shortest = self if self_is_shortest else other
        # Get the max num characters in both objects and add missing whitespaces to keep alignments
        for obj in [shortest, longest]:
            width = obj.width()
            for i in range(len(obj)):
                obj[i] = obj[i].ljust(width)
        # Compute size difference
        size_diff = longest.width() - shortest.width()
        if size_diff == 0:
            return self, other
        # Add extra whitespaces
        shortest.laddblank(int(math.floor(0.5 * size_diff)))
        shortest.raddblank(size_diff - int(math.floor(0.5 * size_diff)))
        # Return the lists in the same order than the input
        if self_is_shortest:
            return shortest, longest
        else:
            return longest, shortest

    def vcenter(self, other):
        """
        Vertical centering: centers the 'self' and 'other' chart boxes vertically
        :param other: other chart box
        :return: 'self' and 'other' inputs in the same order
        """
        # Identify the longest and shortest lists
        self_is_shortest = len(self) < len(other)
        longest = other if self_is_shortest else self
        shortest = self if self_is_shortest else other
        # Get the max num characters in both lists and add missing whitespaces to keep alignments
        for obj in [shortest, longest]:
            width = obj.width()
            for i in range(len(obj)):
                obj[i] = obj[i].ljust(width)
        # Compute size difference
        size_diff = len(longest) - len(shortest)
        if size_diff == 0:
            return self, other
        # Add extra strings to the shortest
        shortest.taddblank(int(math.floor(0.5 * size_diff)))
        shortest.baddblank(size_diff - int(math.floor(0.5 * size_diff)))
        # Return the lists in the same order than the input
        if self_is_shortest:
            return shortest, longest
        else:
            return longest, shortest

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
        self._strings = [joinchar.join(self._strings)]
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


class GenericChart(ABC):
    """
    This is the broadest and most generic implementation of a chart
    It only implements standard methods
    """
    def __init__(self, height=20):
        if not isinstance(height, int) or height < 5:
            raise ValueError('height should be an integer value and should be greater than 5')
        self._height = height
        self.left_margin_size = 5

    @abstractmethod
    def figurebox(self, data):
        pass

    @abstractmethod
    def legendbox(self, legend, legendpos):
        pass

    @abstractmethod
    def yaxis(self, data, ticks, numticks):
        pass

    def plot(self, data, labels=None, legend=None, legendpos='right', numticks=5, ticks='auto', title=None):
        """
        The most generic plotting function
        It relies on the assumption that the  chart is composed on the following boxes:
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
        # Generate chart boxes
        yaxis = self.yaxis(data, ticks, numticks)
        figurebox = self.figurebox(data)
        legendbox = self.legendbox(legend, legendpos)
        figurefooterbox = self.figurefooterbox(data, labels)
        # Concatenate the figure footer inside the figure box,
        # then add the missing extra blank rows to the y axis
        hasfooter = not figurefooterbox.isempty()
        figurebox_size = len(figurebox)
        if hasfooter:
            figurebox.tconcat(figurefooterbox.reverse())
        yaxis.taddblank(len(figurebox) - figurebox_size)
        # Concanate the y axis inside the figure box, then reverse the figure box
        figurebox.lconcat(yaxis).reverse()
        # If the legend is on the right:
        # - add a few blank characters to separate it from the figure
        # - center the figure and legend boxes vertically
        # - and concatenate them
        if legend is not None and legendpos == 'right':
            legendbox.laddblank(5)
            figurebox, legendbox = figurebox.vcenter(legendbox)
            figurebox.rconcat(legendbox)
        # If the legend is on the top or the bottom:
        # - put the legend in a single line
        # - add a few blank lines to separate it from the figure
        # - center the figure and the legend boxes horizontally
        # - and concatenate them
        if legend is not None and legendpos in ['top', 'bottom']:
            legendbox.join(RichText(' ' * 5))
            figurebox, legendbox = figurebox.hcenter(legendbox)
            if legendpos == 'top':
                figurebox.tconcat(legendbox.baddblank(2))
            else:
                figurebox.bconcat(legendbox.taddblank(2))
        # Create the title box
        hastitle = title is not None and len(title) > 0
        if hastitle:
            titlebox = ChartBox()
            titlebox.append(title if isinstance(title, RichText) else RichText(title, style='bold'))
            titlebox, figurebox = titlebox.hcenter(figurebox)
            figurebox.tconcat(titlebox.baddblank(2))

        # Add some margins: blank line above the figure and left margin
        figurebox.taddblank(1)
        figurebox.laddblank(self.left_margin_size)

        # Now actually print the chart
        print(figurebox)


class Bars(GenericChart):
    """
    Standard bar chart
    """

    def __init__(self, color='blue', height=20, showvalues=False, spacing=2, thickness=5, ymax=None):
        super(Bars, self).__init__(height)
        self._color = color
        self._showvalues = showvalues
        self._spacing = spacing
        self._thickness = thickness
        self._ymax = ymax

    def figurebox(self, data):
        """
        :param data:
        :return: ChartBox
        """
        num_bars = len(data)
        ycoords, dy = self.ycoordinates(data)
        # Determine the figure's width
        width = num_bars * self._thickness + (num_bars + 1) * self._spacing
        # Build the figure box and initialize it with the x axis
        figure_box = ChartBox()
        # Draw the figure
        for j in range(len(ycoords)):
            if ycoords[j] == 0:
                figure_box.append([RichText('-' * width, style='bold')])
            else:
                ysign = 1 if ycoords[j] >= 0 else -1
                # For coloring, we take the middle of the cell into account
                # --> subtract 0.5 * dy for positive y and add 0.5 * dy for negative y
                y = ycoords[j] - 0.5 * ysign * dy
                s = RichText(' ' * self._spacing)  # add the first spacing
                for i in range(num_bars):
                    color = _getcolor(self._color, i, y)
                    if 0 <= y <= data[i] or 0 >= y >= data[i]:
                        s += RichText(' ' * self._thickness, bg=color)
                    elif ycoords[j] == dy and 0 <= data[i] <= y:
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
                # Center the value string in the middle of the bar
                valuestr = RichText(str(NiceNumber(data[i]))).center(bar_stop[i] - bar_start[i], pushleft=True)
                color = _getcolor(self._color, i, ycoords[max(j-1, 0)] - 0.5 * dy)
                if j == 1:
                    valuestr = RichText(valuestr, fg=color, style='bold+underline')
                else:
                    valuestr = RichText(valuestr, fg=color, style='bold')
                figure_box[j] = figure_box[j][0:bar_start[i]] + valuestr + figure_box[j][bar_stop[i]:]
        return figure_box

    def figurefooterbox(self, data, labels):
        """
        Creates a figure footer cbart box to put input labels beneath the figure's bars
        :param labels: list of strings
        :return: ChartBox object
        """
        if labels is None:
            return ChartBox()
        # Build a single string containing input labels at the right positions
        footer_str = [RichText('')]
        num_bars = len(data)
        # TODO Check input labels
        # Add labels
        for i in range(num_bars):
            current_label = labels[i]
            # Start and stop indices of the current bar
            start = self._spacing + i * (self._thickness + self._spacing)
            stop = start + self._thickness
            if len(current_label) > stop - start:
                # If the label is too long, try splitting it first
                current_label = current_label.split(' ')
                # If it is still to long, skip this label
                if max(len(s) for s in current_label) > stop - start:
                    continue
                # Try to bring some pieces together
                idx = 0
                while idx < len(current_label) - 1:
                    merged_labels = ' '.join(current_label[idx:idx+2])
                    if len(merged_labels) <= stop - start:
                        current_label[idx] = merged_labels
                        del current_label[idx+1]
                    else:
                        idx += 1
            else:
                # Otherwise put the label in a list with a single element
                # This is just to have the same data structure as when the label does not fit
                current_label = [current_label]
            # Add the parts of the label to the footer string
            for j in range(len(current_label)):
                if j >= len(footer_str):
                    footer_str.append(RichText(''))
                footer_str[j].ljust(start)
                footer_str[j] += RichText(current_label[j], style='bold').center(stop - start, pushleft=True)
        # Create the output object
        figure_footer_box = ChartBox()
        figure_footer_box.append(footer_str)
        return figure_footer_box

    def legendbox(self, labels, legendpos):
        """
        Simple bar charts don't support legends
        :param labels:
        :param legendpos:
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
        ycoords, _ = self.ycoordinates(data)
        has_pos_coords = sum(1 for y in ycoords if y > 0) > 0
        has_neg_coords = sum(1 for y in ycoords if y < 0) > 0
        # Compute ticks
        if ticks is not None:
            tick_indices, numchar = get_tick_indices(ticks, numticks, ycoords)
        else:
            tick_indices = []
            numchar = 0
        # Create the y axis
        yaxis = ChartBox()
        # TODO add comment to explain why we use height + showvalues below
        num_extra_rows = int(self._showvalues) * (int(has_pos_coords) + int(has_neg_coords))
        axis_size = len(ycoords) + num_extra_rows
        for j in range(axis_size):
            s = ''
            if ticks is not None:
                if j in tick_indices:
                    # Put a tick on the current line
                    s += str(NiceNumber(ycoords[j])).rjust(numchar)
                else:
                    # No tick on current line --> add extra spaces to keep alignment
                    s += numchar * ' '
            # Add the y axis marker
            no_axis_marker = self._showvalues and ((j == 0 and has_neg_coords) or (j == axis_size - 1 and has_pos_coords))
            s += '|' if not no_axis_marker else ' '
            yaxis.append(RichText(s, style='bold'))
        return yaxis

    def ycoordinates(self, data):
        """
        Compute y coordinates
        :param data: data to plot
        :return ycoords: list of y coordinates in ascending order
        :return dy: spacing along the y axis
        """
        # Get the max y value
        ymax = max(data)
        if self._ymax is not None:
            ymax = max(ymax, self._ymax)
        # Compute the spacing along the y axis
        dy = ymax / (self._height * 1.0)
        # Compute the y coordinates
        ycoords = [i * dy for i in range(self._height + 1)]
        # Enforce the max value as last element to prevent round off errors
        ycoords[-1] = ymax
        return ycoords, dy


class StackedBars(Bars):

    def __init__(self, height=20, spacing=2, thickness=5):
        super(StackedBars, self).__init__(height=height, spacing=spacing, thickness=thickness)

    def colorpalette(self):
        """
        Return the list of all colors through which we are going to cycle
        :return: list of colors
        """
        return ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']

    def coloring(self, y, dictionary, categories):
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
        :param legendpos: legend position, should be 'top', 'bottom' or 'right'
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

    def plot(self, data, legendpos='right', numticks=5, ticks='auto', title=None):
        """
        Create the plot
        :param data: list of non-empty dictionaries
        :param ticks: y axis ticks
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
        self._color = lambda idx, y: self.coloring(y, data[idx], categories)
        super(StackedBars, self).plot(
            [sum(d.values()) for d in data],
            legend=categories, legendpos=legendpos, numticks=numticks, ticks=ticks, title=title)


class PercentageStackedBars(StackedBars):

    def __init__(self, height=20, spacing=2, thickness=5):
        super(PercentageStackedBars, self).__init__(height, spacing, thickness)

    def plot(self, data, legendpos='right', numticks=5, ticks='all', title=None):
        """
        Create the plot
        :param data: list of non-empty dictionaries
        :param legendpos: legend position, should be 'top', 'bottom' or 'right'
        :param numticks: minimum number of ticks to display
        :param ticks: y axis ticks, should be 'all' (default), 'auto' or a list of numeric values
        :param title: string, figure title
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
        self._color = lambda idx, y: self.coloring(y, data[idx], categories)
        super(StackedBars, self).plot(
            [100] * len(data),  # with stacked bars, we only plot bars of size 100
            legend=categories, legendpos=legendpos, numticks=numticks, ticks=ticks, title=title)


class PositiveNegativeBars(Bars):

    def __init__(self, color=lambda index, y: 'red' if y < 0 else 'green', height=20, showvalues=False, spacing=2,
                 thickness=5, ymax=None, ymin=None):
        super(PositiveNegativeBars, self).__init__(
            height=height, color=color, showvalues=showvalues, spacing=spacing, thickness=thickness, ymax=ymax)
        self._ymin = ymin



    def legendbox(self, labels, legendpos):
        """
        Positive negative bar charts do not support legends --> return an empty chart box
        :param labels:
        :param legendpos:
        :return:
        """
        return ChartBox()


    def ycoordinates(self, data):
        """
        Compute y coordinates
        :param data: list of numeric values to plot
        :return ycoords: list of y coordinates in ascending order
        :return dy: spacing along the y axis
        """
        # Get min and max y values
        ymax = max(data) if self._ymax is None else max(max(data), self._ymax)
        ymin = min(data) if self._ymin is None else min(min(data), self._ymin)
        # Compute the spacing along the y axis
        maxbound = max(ymax, abs(ymin))
        minbound = min(ymax, abs(ymin))
        dy = maxbound / round(maxbound / (ymax - ymin) * self._height)
        # Number of cells on the plus and minus sides
        pnumcells = round(maxbound / (ymax - ymin) * self._height)
        mnumcells = math.ceil(minbound / dy)
        if maxbound == abs(ymin):
            pnumcells, mnumcells = mnumcells, pnumcells
        # Compute y coordinates
        ycoords = [-i * dy for i in range(mnumcells, 0, -1)] + [i * dy for i in range(1, pnumcells + 1)]
        # Adjust height
        self._height = len(ycoords)
        # Compute the y coordinates
        # Enforce the min and max values as last element to prevent round off errors
        if maxbound == abs(ymin):
            ycoords[0] = ymin
        if maxbound == ymax:
            ycoords[-1] = ymax
        return ycoords, dy
