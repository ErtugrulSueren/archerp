
import frappe
from frappe.utils import getdate, add_to_date, flt
from frappe.utils.dateutils import get_period, get_period_beginning

def get_data(chart, filters=None, values=None, time_interval=None, timespan=None, from_date=None, to_date=None):
    """
    Custom Chart Source to calculate Sales Trend (base_grand_total sum)
    Bypassing field-level permissions.
    """
    
    # 1. Determine Date Range and Interval
    # Default to Monthly if not provided
    if not time_interval:
        time_interval = chart.time_interval or "Monthly"
        
    # Handle Date Range
    if not (from_date and to_date):
        # Default logic (e.g. Last Year) if simple args missing, 
        # but configured chart usually sends valid from/to if timespan is set.
        # Fallback to last 1 year
        to_date = getdate()
        from_date = add_to_date(to_date, years=-1)
    else:
        from_date = getdate(from_date)
        to_date = getdate(to_date)

    # 2. Get Data Bypassing Permissions (but respecting Doc Perm)
    data = get_sales_data(from_date, to_date, time_interval)
    
    # 3. Format strictly for Frappe Charts
    # result structure: { "labels": [...], "datasets": [{"name": "...", "values": [...]}] }
    
    labels = []
    values = []
    
    # Generate continuous timeline
    current_date = from_date
    while current_date <= to_date:
        period = get_period(current_date, time_interval)
        label = format_label(current_date, time_interval)
        
        if label not in labels:
            labels.append(label)
            # Find value for this period
            val = next((d['total'] for d in data if d['period'] == period), 0.0)
            values.append(val)
            
        # Increment
        current_date = add_to_date(current_date, **get_interval_increment(time_interval))

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Toplam Ciro",
                "values": values,
                "chartType": "bar" 
            }
        ],
        "type": "bar" # Default type, but config in __init__.py overrides this with chart_doc.type usually
        # But wait, if chart_doc.type is Custom, frontend might rely on this return? 
        # No, my fix in __init__.py passes chart_doc.type (which is stuck to "Custom" now?)
        # AH! If chart_doc.chart_type is Custom, chart_doc.type (visual type like Bar/Line) might still be relevant?
        # Let's check chart_doc.type. It exists.
        # So frontend will receive "Bar" (or whatever was set) if my __init__.py fix works.
    }

def get_sales_data(from_date, to_date, time_interval):
    # Allowed docs
    allowed_docs = frappe.get_list("Satis Faturasi", pluck="name")
    if not allowed_docs:
        return []
        
    sf = frappe.qb.DocType("Satis Faturasi")
    from frappe.query_builder.functions import Sum, Date
    
    # We need to Group By Period based on interval. 
    # This is tricky in DB agnostic way. 
    # Simplified: Fetch row-based Date and Sum, then aggregate in Python for safety/simplicity
    # OR use Frappe's grouping utils?
    # Let's aggregate in Python to avoid DB-specific SQL functions for months/quarters issues.
    
    query = (
        frappe.qb.from_(sf)
        .select(sf.fatura_tarihi, sf.base_grand_total)
        .where(sf.name.isin(allowed_docs))
        .where(sf.docstatus == 1)
        .where(sf.fatura_tarihi.between(from_date, to_date))
    )
    
    rows = query.run(as_dict=True)
    
    # Aggregate in memory
    aggregated = {}
    
    for row in rows:
        if not row.fatura_tarihi: continue
        period = get_period(row.fatura_tarihi, time_interval)
        aggregated.setdefault(period, 0.0)
        aggregated[period] += flt(row.base_grand_total)
        
    # Convert to list
    return [{"period": k, "total": v} for k, v in aggregated.items()]

def format_label(date, interval):
    from frappe.utils import formatdate
    return formatdate(date, "MMM YYYY" if interval in ["Monthly", "Quarterly"] else "dd-MM-YYYY")

def get_interval_increment(interval):
    if interval == "Monthly": return {"months": 1}
    if interval == "Weekly": return {"weeks": 1}
    if interval == "Yearly": return {"years": 1}
    if interval == "Quarterly": return {"months": 3}
    return {"days": 1}
