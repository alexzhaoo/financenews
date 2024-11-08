import pandas as pd


def filter(input_file, output_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Filter the DataFrame to include only articles with '' in the title
    keywords = [
        'stock', 'inflation', 'recession', 'stocks', 'bonds', 'markets', 'interest', 
        'credit', 'liquidity', 'debt', 'revenue', 'capital', 'trade', 'deficit', 
        'tariffs', 'growth', 'currency', 'profit', 'equity', 'policy', 'taxes', 
        'risk', 'yield', 'assets', 'futures', 'investment', 'diversification', 
        'hedge', 'reserve', 'index', 'rates' , 'earnings' , 'cost', 'valuation', 'volatility'
        , 'commodities', 'currencies', 'inflation', 'deflation', 'economy', 'economic',
        'market', 'financial', 'finance', 'money', 'investment', 'investing', 'investor',
        'investors', 'portfolio', 'fund', 'funds', 'asset', 'assets', 'wealth', 'capital',
        'equity', 'equities', 'bond', 'bonds', 'stock', 'stocks', 'stock market', 'stock markets',
        'commodity', 'commodities', 'currency', 'currencies', 'derivative', 'derivatives',
        'option', 'options', 'future', 'futures', 'swap', 'swaps', 'interest rate', 'interest rates',
        'credit', 'credits', 'loan', 'loans', 'mortgage', 'mortgages', 'bank', 'banks', 'banking',
        'financial institution', 'financial institutions', 'insurance', 'insurances', 'hedge fund',
        'hedge funds', 'private equity', 'private equities', 'venture capital', 'venture capitals',
        'mutual fund', 'mutual funds', 'exchange-traded fund', 'exchange-traded funds', 'ETF',
        'ETFs', 'real estate', 'real estates', 'property', 'properties', 'investment trust',
        'investment trusts', 'investment company', 'investment companies', 'investment bank',
        'investment banks', 'investment banking', 'investment banker', 'investment bankers',
        'investment advisory', 'investment advisor', 'investment advisors', 'investment management',
        'investment manager', 'investment managers', 'investment portfolio', 'investment portfolios',
        'investment strategy', 'investment strategies', 'investment decision', 'investment decisions',
        '%', '$' , '£', '€', '¥', '₹', '₽', '₿', '₺'
    ]
    pattern = '|'.join(keywords)
    filtered_df = df[df['title'].str.contains(pattern, case=False, na=False)]

    # Write the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_file, index=False)


# Filter the data
filter('CNBCHomepageNews.csv', 'filtered_articles.csv')

    


