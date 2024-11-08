import pandas as pd

def cut_csv_rows_by_half(input_csv_path, output_csv_path):
    # Read the CSV file
    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')
    
    # Calculate the midpoint
    midpoint = len(df) // 2
    
    # Cut the dataframe by half
    df_half = df.iloc[:midpoint]
    
    # Save the new dataframe to a new CSV file
    df_half.to_csv(output_csv_path, index=False)


cut_csv_rows_by_half('../all-data.csv', '../all-data.csv')
cut_csv_rows_by_half('../dataset.csv', '../dataset.csv')