
# Dashboard Logic Package

import frappe
from frappe import _
from frappe.desk.doctype.number_card.number_card import get_result as get_number_card_result
from frappe.desk.doctype.dashboard_chart.dashboard_chart import get as get_chart_data

@frappe.whitelist()
def get_dashboard_config(from_date=None, to_date=None):
    """
    Fetches the dashboard configuration for the current user based on their roles.
    Resolves conflicts using 'priority' (High wins).
    Applies date filters to cards and charts.
    """
    from frappe.utils import getdate
    
    if from_date: from_date = getdate(from_date)
    if to_date: to_date = getdate(to_date)
    
    user_roles = frappe.get_roles(frappe.session.user)
    
    # 1. Fetch all dashboards sorted by Priority DESC
    # Higher priority comes first, so the first match wins.
    dashboards = frappe.get_all("Portal Dashboard", fields=["name"], order_by="priority desc")
    
    selected_dashboard = None
    
    for d in dashboards:
        doc = frappe.get_doc("Portal Dashboard", d.name)
        
        # Check roles
        allowed_roles = [r.role for r in doc.roles]
        
        if not allowed_roles:
             # Strict: Must have role.
             pass
        elif any(role in user_roles for role in allowed_roles):
            selected_dashboard = doc
            break
            
    if not selected_dashboard:
        return None
        
    config = {
        "name": selected_dashboard.dashboard_name,
        "shortcuts": [],
        "cards": [],
        "charts": []
    }
    
    # Prepare Filters
    filters = {}
    if from_date: filters["from_date"] = from_date
    if to_date: filters["to_date"] = to_date
    
    # Process Shortcuts
    for sc in selected_dashboard.shortcuts:
        config["shortcuts"].append({
            "label": sc.label,
            "icon": sc.icon,
            "reference_doctype": sc.reference_doctype,
            "view_type": sc.view_type,
            "color": sc.color
        })
    
    # 2. Process Cards
    # Sort by idx in Child Table
    selected_dashboard.cards.sort(key=lambda x: x.idx)
    
    for row in selected_dashboard.cards:
        if not row.card: continue
        
        try:
             card_doc = frappe.get_doc("Number Card", row.card)
             
             value = 0
             
             if card_doc.type == 'Custom' and card_doc.method:
                 # Execute Custom Method
                 try:
                     method_filters = {"from_date": from_date, "to_date": to_date}
                     value = frappe.call(card_doc.method, filters=method_filters)
                 except Exception as custom_err:
                     frappe.log_error(f"Custom Card method failed {row.card}: {custom_err}")
                     value = 0
             else:
                 # Standard Card Logic
                 # 1. Start with existing card filters (from UI config)
                 card_filters = []
                 if card_doc.filters_json:
                     import json
                     try:
                         existing_filters = json.loads(card_doc.filters_json)
                         if isinstance(existing_filters, list):
                             card_filters.extend(existing_filters)
                     except:
                         pass

                 # 2. Add Date components if selected
                 if from_date and to_date:
                     # BUG FIX: aggregate_function_based_on is for SUMming, not for filtering dates!
                     # We must find the correct Date field (e.g. fatura_tarihi) independently.
                     date_field = None
                     
                     # Smart detect common date fields
                     if card_doc.document_type:
                        try:
                             meta = frappe.get_meta(card_doc.document_type)
                             for candidate in ["posting_date", "tarih", "fatura_tarihi", "transaction_date"]:
                                if meta.has_field(candidate):
                                    date_field = candidate
                                    break
                        except:
                            pass
                     
                     date_field = date_field or "creation"
                     
                     # Ensure we filter on the correct doc
                     if card_doc.document_type:
                        card_filters.append([card_doc.document_type, date_field, "between", [from_date, to_date]])
                 
                 # Pass ONLY the merged filters. 
                 # We send to_date=None to disable get_result's hardcoded 'creation' logic.
                 value = get_number_card_result(card_doc, filters=card_filters, to_date=None)
             
             config["cards"].append({
                 "name": card_doc.name,
                 "label": card_doc.label,
                 "value": value,
                 "color": card_doc.color,
                 "icon": getattr(card_doc, 'icon', None) or "box"
             })
        except Exception as e:
            frappe.log_error(f"Error fetching card {row.card}: {str(e)}")
            
    # 3. Process Charts
    # Sort by idx
    selected_dashboard.charts.sort(key=lambda x: x.idx)

    for row in selected_dashboard.charts:
        if not row.chart: continue
        
        try:
            # Fetch doc to get the explicit TYPE (Pie, Bar, etc.)
            chart_doc = frappe.get_doc("Dashboard Chart", row.chart)
            
            # Dashboard Chart 'get' method accepts from_date and to_date args directly
            data = get_chart_data(
                chart_name=row.chart, 
                from_date=from_date, 
                to_date=to_date
            )
            
            config["charts"].append({
                "name": row.chart,
                "title": chart_doc.chart_name,
                "data": data,
                "type": chart_doc.type # Passing explicit type from Doc
            })
        except Exception as e:
            frappe.log_error(f"Error fetching chart {row.chart}: {str(e)}")
            config["charts"].append({
                "name": row.chart,
                "title": f"Error: {str(e)}", 
                "data": {"labels": [], "datasets": []},
                "type": "bar",
                "manual_error": str(e)
            })
            
    return config

