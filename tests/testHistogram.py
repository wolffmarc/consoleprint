from Histogram import *
import random
import string

sb = StackedBars(height=20)
sb.plot([{'A': 5, 'B': 12}, {'A': 7, 'C':15}, {'B': 36}, {'C': 4, 'D': 87}], ticks='all')


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
bars = Bars(height=10, color=colorfun, spacing=1, thickness=3, ymax=100)
bars.plot(data, ticks='auto', numticks=5)
bars.plot(data, ticks='all')
bars = Bars(height=12, color=colorfun, spacing=1, thickness=3, ymax=120)
bars.plot(data, ticks='auto', numticks=5)
bars.plot(data, ticks='all')
bars = Bars(height=10, color=colorfun, spacing=1, thickness=3, showvalues=True, ymax=100)
bars.plot(data, ticks='auto', numticks=5)
bars.plot(data, ticks='all')
bars = Bars(height=12, color=colorfun, spacing=1, thickness=3, showvalues=True, ymax=120)
bars.plot(data, ticks='all')



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
sb = StackedBars(20, spacing=1, thickness=3)
sb.plot(data, legendpos='top', title='Stacked bars with legend above the figure'.title())
sb.plot(data, legendpos='right', title='Stacked bars with legend on the right'.title())
sb.plot(data, legendpos='bottom', title='Stacked bars with legend below the figure'.title())
sb.plot(data, legendpos='top', numticks=5, title='Stacked bars with legend above the figure'.title())
sb.plot(data, legendpos='top', numticks=10, title='Stacked bars with legend above the figure'.title())

sb = PercentageStackedBars(height=20, spacing=1, thickness=3)
sb.plot(data, legendpos='top', title='Percentage stacked bars with legend above the figure'.title())
sb.plot(data, legendpos='right', title='Percentage stacked bars with legend on the right'.title())
sb.plot(data, legendpos='bottom', title='Percentage stacked bars with legend below the figure'.title())