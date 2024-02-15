import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from  matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages
import plotly.graph_objects as go

def export_table_plot(cell_values_df, color_values_df, pdf_filename, boldface_ranges = None, p_values_df = None, hide_rows = None, figsize=(10, 7), colorbar_label: str=None):
    # Assuming cell_values_df contains the color values and color_values_df contains the values to display
    # Ranges is a list of column indexes if wanting to boldface the maximum value in a subset of the columns


    # Hide rows by name 
    if hide_rows is not None:
        cell_values_df = cell_values_df.drop(hide_rows)
        color_values_df = color_values_df.drop(hide_rows)
        if p_values_df is not None:
            p_values_df = p_values_df.drop(hide_rows)


    # Set up the color map
    cmap=LinearSegmentedColormap.from_list('rg',["r", "w", "g"], N=256) 


    # Create a diverging color bar
    norm = plt.Normalize(-1, 1)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])


    # Plot the table with assigned colors
    fig, ax = plt.subplots(figsize=figsize)
    table = plt.table(cellText=cell_values_df.values, cellColours=plt.cm.get_cmap(cmap)(norm(color_values_df.values)),
                    cellLoc='center', colLabels=cell_values_df.columns, rowLabels=cell_values_df.index, loc='center', bbox=[0, 0, 1, 1])

    # Add significance
    if p_values_df is not None:
        for i in range(len(cell_values_df)):
            for j in range(len(cell_values_df.columns)):
                value, p_val = str(cell_values_df.iloc[i, j]), p_values_df.iloc[i, j]
                if p_val < 0.001:
                    value += "$^{{**}}$"
                elif p_val < 0.05:
                    value += "$^*$"
                table[i + 1, j].get_text().set_text(value)

    # Boldface highest value in each row (by columns subset, if ranges)
    if not boldface_ranges:
        # from all values in the row
        boldface_ranges = [0, cell_values_df.shape[1]]
    for i, row in enumerate(cell_values_df.values):
        for j in range(len(boldface_ranges)-1):
            max_idx = row[boldface_ranges[j]:boldface_ranges[j+1]].argmax()
            table[i+1, boldface_ranges[j] + max_idx].get_text().set_weight('bold')
    
    
    # Add color bar
    cbar = fig.colorbar(sm, ax=ax, pad=0.02)
    cbar.set_label(colorbar_label)

    # Hide axes
    ax.axis('off')

    # Export to PDF
    with PdfPages(pdf_filename) as pdf:
        pdf.savefig(fig, bbox_inches='tight')

    plt.close()

    print(f'Table plot exported to {pdf_filename}.')


def export_frequency_plot(df, col1, col2, order,  colors, labels_type, pdf_filename):
    # Calculate frequencies
    freq_col1 = df[col1].value_counts(normalize=True) * 100
    sorted_freq1 = freq_col1.reindex(order, fill_value=0)
    # print(freq_col1.sum())
    freq_col2 = df[col2].value_counts(normalize=True) * 100
    sorted_freq2 = freq_col2.reindex(order, fill_value=0)

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))


    # Plot bars for column1
    bars1 = ax.barh(order, -sorted_freq1, color='blue', label='Phase 1')

    # Plot bars for column2
    bars2= ax.barh(order, sorted_freq2, color='orange', label='Phase 2')

    # Display percentages in each bar
    for i, (bar1, freq1, bar2, freq2) in enumerate(zip(bars1, sorted_freq1, bars2, sorted_freq2)):
        ax.text(bar1.get_width() - 7.5, bar1.get_y() + bar1.get_height() / 2, f'{freq1:.2f}%', va='center', ha='left', color='blue')
        ax.text(bar2.get_width() + 7, bar2.get_y() + bar2.get_height() / 2, f'{freq2:.2f}%', va='center', ha='right', color='orange')

    # Set X-axis labels and legend
    #ax.set_xlabel('Percentage')
    ax.set_xlim(-50, 45)
    ax.set_xticks(list(range(-40, 0, 10))+list(range(0, 50, 10)))
    ax.set_xticklabels(list(range(40, 0, -10))+list(range(0, 50, 10)))
    ax.set_title(labels_type)
    ax.legend()

    # Set Y-axis labels and background colors
    yticks = [i for i in range(len(order))]
    ax.set_yticks(yticks)
    ax.set_yticklabels([' '.join(l.split('_')) for l in order], ha='right', color='black', fontsize=10)
    # Add background color rectangles (yticks_color)
    for i, color in enumerate(colors):
        rect = plt.Rectangle((-70, i - 0.5), 20, 1, linewidth=0, edgecolor='none', facecolor=color, alpha=0.3, clip_on=False) 
        ax.add_patch(rect)
    # Remove the border of the Y-axis
    #ax.spines['left'].set_visible(False)
    #ax.spines['right'].set_visible(False)


    # Export to PDF
    with PdfPages(pdf_filename) as pdf:
        pdf.savefig(fig, bbox_inches='tight')

    plt.close()

    print(f'Bar plot exported to {pdf_filename}.')


def export_alluvial_diagram(df, col1, col2, order, labels_type, pdf_filename):

    # Calculate the links between nodes
    values_1, values_2, counts = [], [], []
    for source in order:
        for target in order:
            value = len(df[(df[col1] == source) & (df[col2] == target)])
            if value > 0:
                values_1.append(source)
                values_2.append(target)
                counts.append(value)

    fig = go.Figure(
        go.Parcats(
            dimensions=[
                {'label': 'Phase 1',
                 'values': values_1},
                 {'label': 'Phase 2', 
                  'values': values_2},
            ],
            counts=counts
        )
    )

    # Set node labels
    fig.update_layout(title_text=labels_type, font_size=10, title_x=0.5, title_y=0.85)


    # Save the plot as a PDF
    fig.write_image(pdf_filename)


def export_sankey_diagram(df, col1, col2, order, colors, labels_type, pdf_filename, opacity=0.9, case=''):
    
    # Create nodes (values in col1 and col2 following order)
    nodes = order + order

    # Create links
    links_src = [nodes.index(df[col1][i]) for i in range(len(df))]
    links_dst = [len(order) + order.index(df[col2][i]) for i in range(len(df))]

    # Create a dict to assign a color with opacity to each node in diagram 
    cmap = {'green': f'rgba(0, 255, 0, {opacity})', 'greenyellow': f'rgba(173,255,47, {opacity})', 'orange': f'rgba(255, 165, 0, {opacity})', 'red': f'rgba(255, 0, 0, {opacity})'}
    node_color = {n: cmap[c] for n, c in zip(order, colors)}

    # Show nodes in the same order for both sides of the step
    nodes_col1 = [n for n in range(0, len(order)) if n in links_src]
    nodes_col2 = [n for n in range(len(order), 2*len(order)) if n in links_dst]
    nodes_x = [0.1] * len(nodes_col1) + [0.9] * len(nodes_col2)
    slots_1 = [x / 10.0 for x in range(1, 10, int(10/len(nodes_col1)))][0:len(nodes_col1)]
    if f"{labels_type}_{case}" == 'gender_all':
        # frequency of occurrence of opinions_two is much larger than opinions_three and overlaps
        print(slots_1)
        slots_1 = [0.1, 0.2] + [c + 0.01 for c in slots_1[2:]]
        print(slots_1)
    slots_2 = [x / 10.0 for x in range(1, 10, int(10/len(nodes_col2)))][0:len(nodes_col2)]
    # if f"{labels_type}_{case}" == 'sexuality_all':
    #     # one less categories (maj unclear) unaligns step
    #     print(slots_2)
    #     slots_2[-2:] = [0.9, 1.0]
    #     print(slots_2)
    nodes_y = slots_1 + slots_2 

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=15,
            thickness=15,
            line=dict(color='black', width=0.5),
            label=nodes, 
            x=nodes_x, 
            y=nodes_y, 
            color=[node_color[val] for val in nodes]
        ),
        link=dict(
            source=links_src,
            target=links_dst,
            value=[1] * len(df),
            color=[node_color[df[col1][i]].replace(str(opacity), "0.2") for i in range(len(df))]
        )
    )])

    # Set node labels
    fig.update_layout(title_text=labels_type, font_size=10, title_x=0.5, title_y=0.75)

    # Save the plot as a PDF
    fig.write_image(pdf_filename)

    print(f'Sankey diagram exported to {pdf_filename}.')


def export_matrix_viz(df, col1, col2, order, labels_type, pdf_filename):
    # Create a pivot table
    pivot_table = pd.crosstab(df[col1], df[col2], margins=True, margins_name='Total')

    # Reorder the pivot table based on the specified order
    pivot_table = pivot_table.reindex(index=order, columns=order, fill_value=0)

    # Create a heatmap using seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    annot = pivot_table.map(lambda x: f'{x}' if x > 0 else '')
    sns.heatmap(pivot_table, annot=annot, fmt='', cmap='Blues', cbar=True, linewidths=.5, vmin=0, vmax=50, ax=ax)

    # Set plot title and labels
    plt.title(labels_type, fontsize=16)
    ax.set(xlabel="Phase 2", ylabel="Phase 1")

    # Export to PDF
    with PdfPages(pdf_filename) as pdf:
        pdf.savefig(fig, bbox_inches='tight')

    plt.close()

    print(f'Matrix exported to {pdf_filename}.')
