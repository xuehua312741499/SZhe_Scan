from sqlinjection import get_html,check_waf
import re

def sqlerror(source):
    sql_errors = {"MySQL": (r"SQL syntax.*MySQL", r"Warning.*mysql_.*", r"MySQL Query fail.*", r"SQL syntax.*MariaDB server"),
                  "PostgreSQL": (r"PostgreSQL.*ERROR", r"Warning.*\Wpg_.*", r"Warning.*PostgreSQL"),
                  "Microsoft SQL Server": (r"OLE DB.* SQL Server", r"(\W|\A)SQL Server.*Driver", r"Warning.*odbc_.*", r"Warning.*mssql_",r"Msg \d+, Level \d+, State \d+", r"Unclosed quotation mark after the character string",r"Microsoft OLE DB Provider for ODBC Drivers"),
                  "Microsoft Access": (r"Microsoft Access Driver", r"Access Database Engine", r"Microsoft JET Database Engine",r".*Syntax error.*query expression"),
                  "Oracle": (r"\bORA-[0-9][0-9][0-9][0-9]", r"Oracle error", r"Warning.*oci_.*", "Microsoft OLE DB Provider for Oracle"),
                  "IBM DB2": (r"CLI Driver.*DB2", r"DB2 SQL error"),
                  "SQLite": (r"SQLite/JDBCDriver", r"System.Data.SQLite.SQLiteException"),
                  "Informix": (r"Warning.*ibase_.*", r"com.informix.jdbc"),
                  "Sybase": (r"Warning.*sybase.*", r"Sybase message")
                }
    for db, errors in sql_errors.items():
        for error in errors:
            pattern=re.compile(error,re.I)
            if pattern.findall(source):
                return True, db
    return False, None

def error_in(domain,queries,old_html):
    payloads = ("'", "')", "';", '"', '")', '";', '`', '`)', '`;', '\\', "%27", "%%2727", "%25%27", "%60", "%5C")
    for payload in payloads:
        website = domain + "?" + ("&".join([param + payload for param in queries]))
        source = get_html.gethtml(website)
        if source:
            vulnerable,db=sqlerror(source)
            if vulnerable and db !=None:
                return True,db
        if check_waf.check_have_waf(old_html, source):
            return False,"waf"
        else:
            return False,None


