from django.http import HttpResponse

def home_view(request):
    html = """
    <h1>Главная страница</h1>
    <ul>
        <li><a href="/author/">Об авторе</a></li>
        <li><a href="/about/">О магазине</a></li>
    </ul>
    """
    return HttpResponse(html)

def author_view(request):
    return HttpResponse("Сайт разработал: Скорик Илья, группа 87ТП")

def about_view(request):
    return HttpResponse('Добро пожаловать в хобби-гипермаркет "Леонард"')