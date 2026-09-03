no_cache = True
template = "templates/pages/epms/tasks.html"

def get_context(context):
    context.no_cache = True
    context.title = "Tasks"
    context.show_sidebar = False
