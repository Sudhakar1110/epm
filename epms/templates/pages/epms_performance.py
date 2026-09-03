no_cache = True
template = "templates/pages/epms/performance.html"

def get_context(context):
    context.no_cache = True
    context.title = "Performance"
    context.show_sidebar = False
