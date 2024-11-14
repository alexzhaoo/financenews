import pandas as pd
import csv

def cut_csv_rows_by_half(input_csv_path, output_csv_path):
    # Read the CSV file
    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')
    
    # Calculate the midpoint
    midpoint = len(df) // 2
    
    # Cut the dataframe by half
    df_half = df.iloc[:midpoint]
    
    # Save the new dataframe to a new CSV file
    df_half.to_csv(output_csv_path, index=False)


# cut_csv_rows_by_half('../all-data.csv', '../all-data.csv')
# cut_csv_rows_by_half('../dataset.csv', '../dataset.csv')

def remove_unwanted_columns(input_csv_path, output_csv_path):
    # Read the CSV file
    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')
    
    # Keep only the specified columns
    df_filtered = df[[ 'Impact', ]]
    
    # Save the new dataframe to a new CSV file
    df_filtered.to_csv(output_csv_path, index=False)


remove_unwanted_columns('../dataset.csv', '../dataset.csv')

def remove_first_column(input_csv_path, output_csv_path):
    # Read the CSV file
    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')
    
    # Remove the first column
    df = df.iloc[:, 1:]
    
    # Save the new dataframe to a new CSV file
    df.to_csv(output_csv_path, index=False)


# remove_first_column('../all-data.csv', '../all-data.csv')

def concatenate_columns(input_csv_path1, input_csv_path2, output_csv_path):
    # Read the first CSV file
    df1 = pd.read_csv(input_csv_path1, encoding='ISO-8859-1')
    
    # Read the second CSV file
    df2 = pd.read_csv(input_csv_path2, encoding='ISO-8859-1')
    
    # Remove the 'Impact' header from df2
    df2.columns = df1.columns
    
    # Concatenate the rows of df1 and df2
    result_df = pd.concat([df1, df2], axis=0)
    
    # Add a label column with 1s
    result_df['Label'] = 1
    
    # Save the new dataframe to a new CSV file
    result_df.to_csv(output_csv_path, index=False)


concatenate_columns('../all-data.csv', '../dataset.csv', '../PositiveLabel.csv')

def quote_every_row(input_csv_path, output_csv_path):
    # Read the CSV file
    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')
    
    # Apply quotes around each row
    df = df.applymap(lambda x: f'"{x}"')
    
    # Save the new dataframe to a new CSV file
    df.to_csv(output_csv_path, index=False, quoting=csv.QUOTE_NONE, escapechar='\\')


# quote_every_row('../NegativeLabel.csv', '../NegativeLabel.csv')

def remove_commas(input_csv_path, output_csv_path):
    # Read the file as plain text
    with open(input_csv_path, 'r', encoding='ISO-8859-1') as file:
        text = file.read()
    
    # Remove all commas
    cleaned_text = text.replace(',', '')
    
    # Write the cleaned text back to a temporary file
    temp_file_path = 'temp_cleaned.csv'
    with open(temp_file_path, 'w', encoding='ISO-8859-1') as file:
        file.write(cleaned_text)
    
    # Read the cleaned text as a DataFrame
    df = pd.read_csv(temp_file_path, delimiter=',')
    
    # Save the DataFrame to the output CSV file
    df.to_csv(output_csv_path, index=False)

# remove_commas('../NegativeLabel.csv', '../NegativeLabel.csv')


