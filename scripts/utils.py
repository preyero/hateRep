import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

def export_table_plot(cell_values_df, color_values_df, pdf_filename, boldface_ranges = None, p_values_df = None, hide_rows = None):
    # Assuming cell_values_df contains the color values and color_values_df contains the values to display
    # Ranges is a list of column indexes if wanting to boldface the maximum value in a subset of the columns


    # Hide rows by name 
    
    # Set up the color map
    cmap = sns.diverging_palette(0, 120, s=80, l=55, n=256, as_cmap=True)

    # Create a diverging color bar
    norm = plt.Normalize(-1, 1)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])


    # Plot the table with assigned colors
    fig, ax = plt.subplots(figsize=(10, 8))
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
    cbar.set_label('Correlation Coefficient')

    # Hide axes
    ax.axis('off')

    # Export to PDF
    with PdfPages(pdf_filename) as pdf:
        pdf.savefig(fig, bbox_inches='tight')

    plt.close()

    print(f'Table plot exported to {pdf_filename}.')
