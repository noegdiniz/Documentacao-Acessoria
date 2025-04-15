from sqlalchemy import inspect
from sqlalchemy import func, desc
from app.ext.db import db

class FilterController:
    @staticmethod
    def filter(content, table):
        filtered_rows = []
        

        # Get the list of column names dynamically
        mapper = inspect(table)
        columns = [column.key for column in mapper.attrs]

        rows_temp = table.query.all()  # Ensure rows are objects with accessible attributes
        rows = []
        
        try:
            for row in rows_temp:
                rows.append(table.query.filter(table.titulo == row.titulo).order_by(table.versao.desc()).first())
        except:
            rows = rows_temp
        
        content_list = content.split(" ") if content else []
        
        # Join all columns into a single string
        for row in rows:
            row.combined_columns = " ".join(str(getattr(row, column)) for column in columns if getattr(row, column) is not None)

        if content: 
            for row in rows:
                for column in columns:
                    # Check if the column is a string
                    if isinstance(getattr(row, column), str):
                        # Check if all of the content_list items are in diferent columns
                        if all(item.lower() in row.combined_columns.lower() for item in content_list):
                            filtered_rows.append(row)
                            break
        else:
            return rows
        
        return filtered_rows
    