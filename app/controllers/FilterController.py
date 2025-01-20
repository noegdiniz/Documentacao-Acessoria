from sqlalchemy import inspect

class FilterController:
    @staticmethod
    def filter(content, table):
        filtered_rows = []
        

        # Get the list of column names dynamically
        mapper = inspect(table)
        columns = [column.key for column in mapper.attrs]

        rows = table.query.all()

        if content:
            for row in rows:
                for column in columns:
                    if content in str(getattr(row, column)):
                        filtered_rows.append(row)
                        break
        
        else:
            return rows
        
        return filtered_rows
    