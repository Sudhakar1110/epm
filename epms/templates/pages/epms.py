no_cache = True
template = "templates/pages/epms/index.html"

def get_context(context):
    context.no_cache = True
    context.title = "EPMS Dashboard"
    context.show_sidebar = False
