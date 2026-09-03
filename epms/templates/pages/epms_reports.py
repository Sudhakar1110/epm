no_cache = True
template = "templates/pages/epms/reports.html"

def get_context(context):
    context.no_cache = True
    context.title = "Reports"
    context.show_sidebar = False
