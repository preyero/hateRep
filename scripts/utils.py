import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

def export_table_plot(cell_values_df, color_values_df, pdf_filename):
    # Assuming df_color contains the color values and df_values contains the values to display
    # Replace 'your_color_column' and 'your_values_column' with the actual column names


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

    # Add color bar
    cbar = fig.colorbar(sm, ax=ax, pad=0.02)
    cbar.set_label('Color Bar Label')

    # Hide axes
    ax.axis('off')

    # Export to PDF
    with PdfPages(pdf_filename) as pdf:
        pdf.savefig(fig, bbox_inches='tight')

    plt.close()

    print(f'Table plot exported to {pdf_filename}.')
