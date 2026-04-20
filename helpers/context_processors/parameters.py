from app.transversal.models import Parameter


def parameters(request):
    result = {}
    try:
        parameters = Parameter.objects.all()
        for item in parameters:
            result[item.key] = item.value

    except Exception:
        pass

    return {'parameters': result}
