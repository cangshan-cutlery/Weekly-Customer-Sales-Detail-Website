from flask import Flask, render_template, request
import pandas as pd
import pyodbc


app = Flask(__name__)
def get_data():
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=EVERWARE4\CBO;DATABASE=SBOCangshan;UID=rog;PWD=d4zNbvcw;Encrypt=optional')
    sql_query = """
	SELECT ORDR.CardCode, ORDR.CardName, RDR1.ItemCode, RDR1.Dscription,
    	sum(RDR1.Quantity) as TotalQuan, sum(RDR1.LineTotal) as TotalAmnt FROM ORDR, RDR1
	WHERE ORDR.DocEntry = RDR1.DocEntry
	AND ORDR.CANCELED <> 'Y'
	AND ORDR.CardName NOT LIKE 'Sample%'
	AND RDR1.ItemCode NOT LIKE 'Replacement%'
	AND RDR1.ItemCode NOT LIKE 'Sample%'
	AND ORDR.CardCode NOT IN ('CA001', 'CA002', 'CA003')
	AND ORDR.DocDate BETWEEN (SELECT CONVERT(NVARCHAR(10), DATEADD(wk,DATEDIFF(wk,7,GETDATE()),0), 120))
                	AND (SELECT CONVERT(NVARCHAR(10), DATEADD(wk,DATEDIFF(wk,7,GETDATE()),6), 120))
	GROUP BY ORDR.CardCode, ORDR.CardName, RDR1.ItemCode, RDR1.Dscription
	ORDER BY CardCode, ItemCode
	"""
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    df_list = []
    for _, group in df.groupby(['CardName']):
        group['OverallTotal'] = group['TotalAmnt'].sum()
        df_list.append(group)
    
    return df_list


@app.route('/')
def display_data():
    search_term = request.args.get('search_card_name') 
    df_list = get_data()
    if search_term:
        df_list = [df for df in df_list if df['CardName'].str.contains(search_term, case=False, na=False).any()]
    return render_template('index.html', df_list=df_list)
if __name__ == '__main__':
     app.run(debug = True)
