from django.shortcuts import render_to_response
from django.views.generic import View


class DocumentationView(View):

    def get(self, request):
        return render_to_response('silk/documentation.html', {
            'request': request
        })