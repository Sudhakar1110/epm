no_cache = True
template = "templates/pages/epms/my_day.html"

def get_context(context):
    context.no_cache = True
    context.title = "My Day"
    context.show_sidebar = False
