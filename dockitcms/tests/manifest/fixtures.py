class ManifestFixtures(object):
    def collection_data_fixture(self):
        return {}
    
    def viewpoint_fixture(self):
        return [{
            "pk": "31",
            "model": "dockitcms.viewpoint",
            "fields": {
                "list_template_html": "",
                "view_type": "dockitcms.listing",
                "url": "/teams/",
                "detail_template_source": "name",
                "mixins": [
                    "widgetblock.widgets"
                ],
                "paginate_by": None,
                "list_template_name": "dockitcms/list.html",
                "detail_template_html": "",
                "detail_template_name": "dockitcms/detail.html",
                "index": "27",
                "list_template_source": "name",
                "widgets": [],
                "slug_field": "",
                "canonical": True,
                "subsite": "29",
                "list_content": "{% for object in object_list %}\r\n<a href=\"{{object.get_absolute_url}}\">{{object}}</a>\r\n{% endfor %}",
                "detail_content": "{% for product in object.products %}\r\n{{product}}\r\n{% endfor %}"
            }
        },
        {
            "pk": "33",
            "model": "dockitcms.viewpoint",
            "fields": {
                "index": "27",
                "view_type": "dockitcms.detailview",
                "url": "/team/",
                "template_name": "dockitcms/detail.html",
                "template_html": "{{ object }} \r\n\r\n{{ object.products }}\r\n",
                "mixins": [],
                "content": "",
                "slug_field": "slug",
                "template_source": "html",
                "subsite": "29",
                "canonical": False
            }
        }]
    
    def application_fixture(self):
        return [{
            "pk": "2",
            "model": "dockitcms.application",
            "fields": {
                "name": "Test",
                "slug": "test",
            }
        }]
    
    def subsite_fixture(self):
        return [{
            "pk": "29",
            "model": "dockitcms.subsite",
            "fields": {
                "widgets": [],
                "url": "/",
                "mixins": [
                    "widgetblock.widgets"
                ],
                "name": "Root",
                "sites": [
                    1
                ]
            }
        }]
    
    def index_fixture(self):
        return [{
            "pk": "27",
            "model": "dockitcms.index",
            "fields": {
                "name": "Team all",
                "parameters": [
                    {
                        "operation": "exact",
                        "key": "slug",
                    }
                ],
                "mixins": [],
                "collection": "4",
                "index_type": "dockitcms.filteredcollection",
                "inclusions": [],
                "exclusions": []
            }
        }]
    
    def collection_fixture(self):
        return [{
            "pk": "4",
            "model": "dockitcms.basecollection",
            "fields": {
                "inherit_from": "",
                "title": "Team",
                "fields": [
                    {
                        "field_type": "ComplexListField",
                        "name": "members",
                        "object_label": "",
                        "fields": [
                            {
                                "field_type": "ComplexListField",
                                "name": "gallery",
                                "object_label": "",
                                "fields": [
                                    {
                                        "field_type": "CharField",
                                        "name": "name",
                                        "default": "",
                                        "blank": False,
                                        "help_text": "",
                                        "null": False,
                                        "verbose_name": ""
                                    },
                                    {
                                        "field_type": "ImageField",
                                        "name": "image",
                                        "default": "",
                                        "upload_to": "",
                                        "blank": False,
                                        "help_text": "",
                                        "null": False,
                                        "verbose_name": ""
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "field_type": "CharField",
                        "name": "name",
                        "default": "",
                        "blank": False,
                        "help_text": "",
                        "null": False,
                        "verbose_name": ""
                    },
                    {
                        "field_type": "SlugField",
                        "name": "slug",
                        "default": "",
                        "blank": False,
                        "help_text": "",
                        "null": False,
                        "verbose_name": ""
                    }
                ],
                "mixins": [],
                "admin_options": {
                    "list_per_page": 100,
                    "list_display": [],
                },
                "application": {'slug':'test'},
                "collection_type": "document",
                "key": "team",
                "object_label": ""
            }
        }]
