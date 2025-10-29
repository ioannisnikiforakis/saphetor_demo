"""
Contains all the views that implement the requested functionality. 
Our urls will be routed to these classes or functions.
"""
from collections import OrderedDict
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from vcfApi.models import VcfRow
from vcfApi.serializers import VcfRowSerializer
from vcfApi import query
from vcfApi import logger
from django.conf import settings

AUTH_HEADER = 'HTTP_AUTHORIZATION'
PREDEFINED_SECRET = settings.PREDEFINED_SECRET

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom Pagination Class implementing the Link requirements
    """
    page_size_query_param = 'page_size'  # items per page
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Override the Paginated response with some useful info and links
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))

def is_authenticated(metadict):
    """
    Get the Authorization header value from the request META and compare it 
    to the predetermined value
    """
    if AUTH_HEADER in metadict:
        app_tk = metadict[AUTH_HEADER]
        return app_tk == PREDEFINED_SECRET
    return False

class VcfRowsList(viewsets.ModelViewSet):
    """
    This Class implements all the List and Create requirements by extending 
    the wired ModelViewset functionality
    """
    queryset = VcfRow.objects.all()
    serializer_class = VcfRowSerializer
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,)
    filterset_fields = {'chrom':['exact'], 'pos':['exact'],'id':['exact','isnull']
            ,'ref':['exact'],'alt':['exact']}
    search_fields = ['chrom','id']
    pagination_class = CustomPageNumberPagination

    def list(self, request):
        """
        Override the default list to implement some of the requirements
        """
        my_filters = query.filter_query(request.META,self.filterset_fields)
        retobjs = self.queryset.filter(**my_filters)
        if retobjs:
            page = self.paginate_queryset(retobjs)
            if page:
                serializer = VcfRowSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = VcfRowSerializer(retobjs, many=True)
            return Response(serializer.data)
        return Response({"detail": "No results found."},
            status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """
        Override the default create to implement authorization checking
        """
        if is_authenticated(request.META):
            data = request.data.copy()
            serializer = VcfRowSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

class VcfRowsDetail(viewsets.ModelViewSet):
    """
    Detail view for VcfRows that takes id as key. 
    This implements the PUT and DELETE Requirements.
    """
    queryset = VcfRow.objects.all()
    serializer_class = VcfRowSerializer
    pagination_class = CustomPageNumberPagination
    lookup_field = "id"

    def retrieve(self, request, id = None, format=None):
        """
        Override the default retrieve to return multiples per the requirement
        """
        try:
            retobjs = VcfRow.objects.filter(id=id)
            if retobjs:
                page = self.paginate_queryset(retobjs)
                if page:
                    serializer = VcfRowSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = VcfRowSerializer(retobjs, many=True)
                return Response(serializer.data)
            return Response({"detail": "No results found."},
                status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.logException(err)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, id = None, format=None):
        """
        Override the default destroy to implement authorization checking
        """
        if is_authenticated(request.META):
            try:
                pkobjs = VcfRow.objects.filter(id=id)
                if len(pkobjs) == 0:
                    return Response({"detail": "No results found."},
                        status=status.HTTP_404_NOT_FOUND)
                for pkobj in pkobjs:
                    pkobj.delete()
            except Exception as err:
                logger.logException(err)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def handle_update_request(self, request, id, partial):
        """
        Performs a validated update on the selected objects
        """
        if is_authenticated(request.META):
            try:
                pkobjs = VcfRow.objects.filter(id=id)
                if len(pkobjs) == 0:
                    return Response({"detail": "No results found."},
                        status=status.HTTP_404_NOT_FOUND)
                data = request.data.copy()
                for pkobj in pkobjs:
                    logger.info(f"Checking {pkobj}")
                    serializer = VcfRowSerializer(pkobj,data=data,partial=partial)
                    if serializer.is_valid():
                        logger.info(f"Saving {pkobj}")
                        serializer.save()
                    else:
                        logger.error(serializer.errors)
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_200_OK)
            except Exception as err:
                logger.logException(err)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, id = None, format=None):
        """
        Override the default PUT update to implement authorization checking
        """
        return self.handle_update_request(request, id, partial=False)

    def partial_update(self, request, id = None, format=None):
        """
        Override the default PATCH update to implement authorization checking
        """
        return self.handle_update_request(request, id, partial=True)
